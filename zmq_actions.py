# -*- coding: utf-8 -*-
from messages import AckMessage, ElectionVoteMessage, NackMessage, UpdateMessage


class Action(object):  # zeroMq specific
    """базовый класс для zmq действий"""

    def send(self, socket, message):
        socket.send(message)

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

    def __repr__(self):
        return str(self.__class__.__name__) + '(' + str(self.__dict__) + ')'


class Ack(Action):
    """Действие - подтверждение"""
    def __init__(self, term, reply_to):
        self.ackMessage = True
        self.term = term
        self.reply_to = reply_to

    def perform(self, socket, sockets, state):
        self.send(socket, AckMessage(self.reply_to.messageId, self.term, self.reply_to))


class BroadcastUpdate(Action):
    """Действие - подтверждение"""
    def __init__(self, term, log, serverStates, leaderCommit, fromLeader):
        self.term = term
        self.log = log
        self.serverStates = serverStates
        self.leaderCommit = leaderCommit
        self.fromLeader = fromLeader

    def perform(self, socket, sockets, state):
        for s in sockets.items():
            self.send(socket, UpdateMessage(
                self.term, self.prevLogIndex, self.prevLogTerm, self.entries,
                self.leaderCommit, self.fromLeader)
            )


class Nack(Action):
    """Действие - отказ"""
    def __init__(self, term, reply_to):
        self.ackMessage = True
        self.term = term
        self.reply_to = reply_to

    def perform(self, socket, sockets, state):
        self.send(socket, NackMessage(self.reply_to.messageId, self.term, self.reply_to))


# election vote
class ElectionVote(Action):
    """Действие - голос 'за' или 'против'"""
    def __init__(self, term, name, voteGranted, reply_to):
        self.term = term
        self.name = name
        self.voteGranted = voteGranted
        self.reply_to = reply_to

    def perform(self, socket, sockets, state):
        self.send(socket, ElectionVoteMessage(self.term, self.name, self.voteGranted, self.reply_to))
