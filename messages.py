# -*- coding: utf-8 -*-
class Message(object):
    def __init__(self):
        self.ackMessage = False
        self.update = False
        self.requestVote = False
        self.election_vote = False

    def __repr__(self):
        return str(self.__class__.__name__) + '(' + str(self.__dict__) + ')'


class AckMessage(Message):
    def __init__(self, messageId, term, reply_to):
        super().__init__()
        self.ackMessage = True
        self.messageId = messageId
        self.term = term
        self.success = True
        self.reply_to = reply_to


class NackMessage(Message):
    def __init__(self, messageId, term, reply_to):
        super().__init__()
        self.ackMessage = True
        self.messageId = messageId
        self.term = term
        self.success = False
        self.reply_to = reply_to


# log update
class UpdateMessage(Message):
    def __init__(self, term, prevLogIndex, prevLogTerm, entries, leaderCommit, fromLeader):
        super().__init__()
        self.update = True
        self.term = term
        self.prevLogIndex = prevLogIndex
        self.prevLogTerm = prevLogTerm
        self.entries = entries
        self.leaderCommit = leaderCommit
        self.fromLeader = fromLeader


# election start
class RequestVoteMessage(Message):
    def __init__(self, term, name, lastLogIndex, lastLogTerm):
        super().__init__()
        self.requestVote = True
        self.term = term
        self.name = name
        self.lastLogIndex = lastLogIndex
        self.lastLogTerm = lastLogTerm


# election vote
class ElectionVoteMessage(Message):
    def __init__(self, term, name, voteGranted, reply_to):
        super().__init__()
        self.election_vote = True
        self.term = term
        self.name = name
        self.voteGranted = voteGranted
        self.reply_to = reply_to
