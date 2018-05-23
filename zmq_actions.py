# -*- coding: utf-8 -*-
from messages import AckMessage, ElectionVoteMessage, NackMessage


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
    def __init__(self,
                 term, reply_to):
        self.ackMessage = True
        self.term = term
        self.reply_to = reply_to

    def perform(self, socket, state):
        self.send(socket, AckMessage(self.reply_to.messageId, self.term, self.reply_to))


class Nack(Action):
    """Действие - отказ"""
    def __init__(self, term, reply_to):
        self.ackMessage = True
        self.term = term
        self.reply_to = reply_to

    def perform(self, socket, state):
        self.send(socket, NackMessage(self.reply_to.messageId, self.term, self.reply_to))


# election vote
class ElectionVote(Action):
    """Действие - голос 'за' или 'против'"""
    def __init__(self, term, name, voteGranted, reply_to):
        self.term = term
        self.name = name
        self.voteGranted = voteGranted
        self.reply_to = reply_to

    def perform(self, socket, state):
        self.send(socket, ElectionVoteMessage(self.term, self.name, self.voteGranted, self.reply_to))
