#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import pickle

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


class Raft(object):
    def __init__(self, server_name, state=None):
        if not state:
            self.state = RaftState(server_name)
        else:
            self.state = state

    # возвращает список действий
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
                return Nack(self.state.commitIndex, self.state.term, message)
            elif self.state.serverRole != 'follower':
                newServerRole = 'follower'
            actions = [
                Ack(message.term, message),
                StateUpdate(message.entries, message.leaderCommit, newServerRole)
            ]
        if message.requestVote:
            try:
                if self.state.log[message.lastLogIndex].term <= message.lastLogTerm:
                    actions = [] #no vote
            except IndexError:
                return [
                    ElectionVote(message.term, self.state.name, message),
                    StateUpdate()
                ]
        pass

        return actions

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


