# -*- coding: utf-8 -*-
from models import AckMessage, ElectionVoteMessage

class Action(object):
    pass

class Ack(Action):

    def __init__(self, commitIndex, messageId, term):
        self.ackMessage = True
        self.messageId = messageId
        self.commitIndex = commitIndex #?
        self.term = term

    def perform(self, socket, state):
        socket.send(AckMessage(self.commitIndex, self.messageId, self.term))


#election vote
class ElectionVote(Action):
    def __init__(self, term, name):
        self.term = term
        self.name = name

    def perform(self, socket, state):
        socket.send(ElectionVoteMessage(self.term, self.name))
