#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from zmq_actions import Ack

class RaftState(object):
    def __init__(self, name):
        self.term = 0
        # self.state = None
        # self.leader = None
        self.votedFor = None
        # self.priority = 1
        # self.power = 1
        self.log = [] # [Command]
        self.commitIndex = 0
        self.lastApplied = 0
        self.name = name
        # leader stuff
        self.serverStates = {} # name -> ServerState

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


    #возвращает список действий
    def recieve(self, update):
        term = update.term
        actions = []
        if update.update:
            prev = update.prev
            new = update.new
            actions.extend([
                Ack(self.state.commitIndex),
            ])
        if update.election_start:
            # vote
            pass

        return actions
