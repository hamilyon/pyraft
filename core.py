#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

import yaml
import zmq

import zeromq_context
from zmq_actions import Ack


class RaftState(object):
    def __init__(self, name):
        self.term = 0
        # self.state = None
        # self.leader = None
        self.votedFor = None
        # self.priority = 1
        # self.power = 1
        self.log = []  # [Command]
        self.commitIndex = 0
        self.lastApplied = 0
        self.name = name
        # leader stuff
        self.serverStates = {}  # name -> ServerState


class ServerState(object):
    def __init__(self, name):
        self.name = name
        self.nextIndex = 0
        self.matchIndex = 0


class Command(object):
    def __init__(self, command, term):
        self.command = command
        self.term = term


class RaftServer(object):
    def __init__(self, name, state=None):
        if not state:
            state = RaftState(name)
        self.state = state

    # возвращает список действий
    def receive(self, message):
        term = message.term
        actions = []
        if message.update:
            prev = message.prev
            new = message.new
            actions.extend([
                Ack(self.state.commitIndex, self.state.term, message),
            ])
        if message.election_start:
            # vote
            pass

        return actions

    def act_upon(self, message):
        actions = self.receive(message)
        for action in actions:
            action.perform()


def pollerThreadRun():
    context = zeromq_context.context
    server_name = sys.argv[1]

    with open("servers.yaml", 'r') as stream:
        config = yaml.load(stream)

    server(server_name, config, context)


def server(server_name, config, context):
    for name in config['servers']:
        server = config['servers'][name]
        if name != server_name:
            print("Connecting to " + name + " server …")
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://" + server)
