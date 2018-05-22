#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Основные структуры данных и чистые функции, реализующие raft (https://raft.github.io/raft.pdf)
ввод-вывод, запись состояния на диск и даже просто изменение состояния должны быть реализованы где-то ещё
"""

import pickle
import sys

import yaml
import zmq

import zeromq_context
from state_actions import StateUpdate
from zmq_actions import Ack, Nack, ElectionVote


class RaftState(object):
    def __init__(self, name):
        self.term = 0 # current term, increases monotonically
        self.serverRole = 'follower' # 'leader', 'candidate', 'follower'
        # self.leader = None
        self.votedFor = None
        # self.priority = 1
        # self.power = 1
        self.log = []  # [Command]
        self.commitIndex = 0
        self.lastApplied = 0
        self.name = name
        # leader stuff
        self.serverStates = {}  # name -> RemoteServerState


class RemoteServerState(object):
    def __init__(self, name):
        self.name = name
        self.nextIndex = 0
        self.matchIndex = 0


class Command(object):
    def __init__(self, command, term):
        self.command = command
        self.term = term

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return str(self.__class__.__name__) + '(' + str(self.__dict__) + ')'


class Raft(object):
    def __init__(self, server_name, state=None):
        if not state:
            self.state = RaftState(server_name)
        else:
            self.state = state

    # returns list of actions
    def receive(self, message):
        term = message.term
        #update term
        newTerm = None
        if self.state.term < term:
            newTerm = term

        actions = []
        if message.update:
            newServerRole = None
            if self.state.term > term:
                return [Nack(self.state.term, message)] #no state update
            elif self.state.serverRole != 'follower':
                newServerRole = 'follower'
            prevLogIndex, prevLogTerm = message.prevLogIndex, message.prevLogTerm
            if len(self.state.log)-1 < prevLogIndex:
                return [Nack(message.term, message)]
            actions = [
                Ack(message.term, message),
                StateUpdate(message.entries, message.leaderCommit, newServerRole, newTerm, prevLogIndex=prevLogIndex)
            ]
        if message.requestVote:
            if message.term > self.state.term:
                try:
                    if message.lastLogIndex == -1 and message.lastLogTerm == -1 and not self.state.log:
                        # log is empty, vote
                        actions = self.vote(message, newTerm)
                    elif self.state.log[message.lastLogIndex].term >= message.lastLogTerm:
                        actions = self.vote(message, newTerm)
                    else:
                        actions = [] #no vote
                except IndexError:
                    actions = self.vote(message, newTerm)  # ok, candidate's log is longer


        return actions

    def vote(self, message, newTerm):
        return [
            ElectionVote(message.term, message.name, message),
            StateUpdate(term=newTerm, votedFor=message.name)
        ]

    def act_upon(self, message):
        actions = self.receive(message)
        for action in actions:
            action.perform()

    def run(self):
        poller = zmq.Poller()
        for socket in self.sockets:
            poller.register(socket, zmq.POLLIN)

        # Work on requests from both server and publisher
        should_continue = True
        while should_continue:
            socks = dict(poller.poll())
            for peer_socket in socks:
                if (socks[peer_socket] == zmq.POLLIN):
                    message = peer_socket.recv()
                    message = pickle.loads(message)
                    print("Recieved command: %s" % message)
                    self.act_upon(message)


class RaftPeer(Raft):
    def __init__(self, server_name, config, context, state=None):
        super().__init__(server_name, state)
        self.config = config
        self.sockets = {}
        for name in config['servers']:
            server_netloc = config['servers'][name]
            if name != server_name:
                print("Connecting to " + name + " server " + server_netloc)
                socket = context.context.socket(zmq.REQ)
                socket.connect("tcp://" + server_netloc)
                self.sockets['name'] = socket
        self.context = context

def run_peer():
    context = zeromq_context.context
    server_name = sys.argv[1]

    with open("servers.yaml", 'r') as stream:
        config = yaml.load(stream)

    peer(server_name, config, context)


def peer(server_name, config, context):
    server_netloc = config['servers'][server_name]
    raft_server = RaftPeer(server_name, config, context)


