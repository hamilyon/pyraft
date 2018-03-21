# -*- coding: utf-8 -*-

class Message(object):
    pass

class AckMessage(Message):
    def __init__(self, commitIndex, messageId, term):
        self.ackMessage = True
        self.messageId = messageId
        self.commitIndex = commitIndex #?
        self.term = term
        self.success = True

class NackMessage(Message):
    def __init__(self, commitIndex, messageId, term):
        self.ackMessage = True
        self.messageId = messageId
        self.commitIndex = commitIndex #?
        self.term = term
        self.success = False

#log update
class UpdateMessage(object):
    def __init__(self, term, prevLogIndex, prevLogTerm, entries, leaderCommit):
        self.update = True
        self.term = term
        self.prevLogIndex = prevLogIndex
        self.prevLogTerm = prevLogTerm
        self.entries = entries
        self.leaderCommit = leaderCommit

#election start
class RequestVoteMessage(object):
    def __init__(self, term, name, lastLogIndex, lastLogTerm):
        self.election_start = True
        self.term = term
        self.name = name
        self.lastLogIndex = lastLogIndex
        self.lastLogTerm = lastLogTerm

#election vote
class ElectionVoteMessage(object):
    def __init__(self, term, name):
        self.election_vote = True
        self.term = term
        self.name = name
        self.voteGranted = True
