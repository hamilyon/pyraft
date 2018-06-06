#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Основные структуры данных и чистые функции, реализующие raft (https://raft.github.io/raft.pdf)
ввод-вывод, запись состояния на диск и даже просто изменение состояния должны быть реализованы где-то ещё
"""

import pickle
import sys
import threading

import time
import yaml
import zmq

import zeromq_context
from messages import ClientUpdate
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
        # term = message.term
        #TODO
        # newTerm = None
        # newServerRole = None
        # if self.state.term < term:
        #     newTerm = term
        #     if self.state.serverRole != 'follower':
        #         newServerRole = 'follower'

        actions = self.dispach_by_type(message)
        return actions

    def vote(self, message, newTerm, voteGranted):
        actions = [
            ElectionVote(message.term, self.state.name, voteGranted, message,),
        ]
        if voteGranted:
            actions.append(StateUpdate(term=newTerm, votedFor=message.name))
        return actions

    def act_upon(self, message, socket):
        actions = self.receive(message)
        for action in actions:
            action.perform(socket, self.state)

    def dispach_by_type(self, message):
        if message.update:
            return self.appendEntriesRpc(message)
        if message.requestVote:
            return self.requestVoteRpc(message)
        return []

    def appendEntriesRpc(self, message):
        term = message.term
        newTerm = max(self.state.term, message.term)

        #TODO move server role to upper function
        newServerRole = None

        if self.state.term < term:
            newTerm = term
            if self.state.serverRole != 'follower':
                newServerRole = 'follower'

        if self.state.term > term:
            return [Nack(self.state.term, message)] #no state update
        prevLogIndex, prevLogTerm = message.prevLogIndex, message.prevLogTerm
        if len(self.state.log)-1 < prevLogIndex:
            return [Nack(message.term, message)]
        if (message.prevLogIndex == -1 and message.prevLogTerm == -1 and not self.state.log) \
                or self.state.log[prevLogIndex].term == prevLogTerm:
            return [
                Ack(message.term, message),
                StateUpdate(message.entries, message.leaderCommit, newServerRole, newTerm, prevLogIndex=prevLogIndex)
            ]
        else:
            return [Nack(message.term, message)]

    def requestVoteRpc(self, message):
        newTerm = max(self.state.term, message.term)
        if message.term < self.state.term:
            return self.vote(message, newTerm, False)
        if message.term > self.state.term or message.name == self.state.votedFor:
            try:
                if message.lastLogIndex == -1 and message.lastLogTerm == -1 and not self.state.log:
                    # log is empty, vote
                    return self.vote(message, newTerm, True)
                elif self.state.log[message.lastLogIndex].term >= message.lastLogTerm:
                    return self.vote(message, newTerm, True)
                else:
                    return self.vote(message, newTerm, False) #negative
            except IndexError:
                return self.vote(message, newTerm, True)  # ok, candidate's log is longer
        else:
            return self.vote(message, newTerm, False) #negative


class RaftPeer(Raft):
    def __init__(self, server_name, config, context, state=None):
        super().__init__(server_name, state)
        self.config = config
        self.sockets = {}
        for name in config['servers']:
            server_netloc = config['servers'][name]
            if name != server_name:
                print("Connecting to " + name + " server " + server_netloc)
                socket = context.socket(zmq.REQ)
                socket.connect("tcp://" + server_netloc)
                self.sockets[name] = socket
            else:
                socket = context.socket(zmq.REP)
                socket.bind("tcp://" + server_netloc)
                self.sockets[name] = socket

        self.context = context

    def run(self):
        poller = zmq.Poller()
        for name, socket in self.sockets.items():
            print('regfistering with poller', socket)
            poller.register(socket, zmq.POLLIN)

        should_continue = True
        while should_continue:
            socks = dict(poller.poll())
            for peer_socket in socks:
                if (socks[peer_socket] == zmq.POLLIN):
                    message = peer_socket.recv()
                    message = pickle.loads(message)
                    print("Recieved command: %s" % message)
                    self.act_upon(message, socket)


def run_peer():
    context = zeromq_context.context
    server_name = sys.argv[1]

    with open("servers.yaml", 'r') as stream:
        config = yaml.load(stream)

    peer(server_name, config, context)


def run_client_emulation_thread(config):
    server_name = sys.argv[1]
    print(server_name)
    threading.Thread(None, client_emulation, None, [config]).start()


def client_emulation(config):
    # hack to wait for to server is up
    time.sleep(0.8)

    context = zeromq_context.context
    socket = context.socket(zmq.REQ)
    print(config)
    socket.connect("tcp://" + config['servers']['first'])
    for i in range(10):
        socket.send_pyobj(ClientUpdate([str(i)]))
        answer = socket.recv_pyobj()
        print(answer)
        print(server.state.log)


server = None


def peer(server_name, config, context):
    print(config, type(config))
    server_netloc = config['servers'][server_name]
    raft_server = RaftPeer(server_name, config, context)
    # hardcode test stuff
    global server
    server = raft_server
    if sys.argv[1] == 'first':
        run_client_emulation_thread(config)

    raft_server.run()



if __name__ == '__main__':
    run_peer()
