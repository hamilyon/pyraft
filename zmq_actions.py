# -*- coding: utf-8 -*-
from models import AckMessage, ElectionVoteMessage, NackMessage


class Action(object):  # zeroMq specific
    """базовый класс для zmq действий"""

    def send(self, socket, message):
        socket.send(message)


class Ack(Action):
    """Действие - подтверждение"""
    def __init__(self, commitIndex, term, reply_to):
        self.ackMessage = True
        self.commitIndex = commitIndex  # ?
        self.term = term
        self.reply_to = reply_to

    def perform(self, socket, state):
        self.send(socket, AckMessage(self.commitIndex, self.reply_to.messageId, self.term, self.reply_to))


class Nack(Action):
    """Действие - отказ"""
    def __init__(self, commitIndex, term, reply_to):
        self.ackMessage = True
        self.commitIndex = commitIndex  # ?
        self.term = term
        self.reply_to = reply_to

    def perform(self, socket, state):
        self.send(socket, NackMessage(self.commitIndex, self.reply_to.messageId, self.term, self.reply_to))


# election vote
class ElectionVote(Action):
    """Действие - голос 'за'"""
    def __init__(self, term, name, reply_to):
        self.term = term
        self.name = name
        self.reply_to = reply_to

    def perform(self, socket, state):
        self.send(socket, ElectionVoteMessage(self.term, self.name, self.reply_to))
