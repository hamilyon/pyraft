# -*- coding: utf-8 -*-
class Message(object):
    pass


class AckMessage(Message):
    def __init__(self,
                 # commitIndex,
                 messageId, term, reply_to):
        self.ackMessage = True
        self.messageId = messageId
        # self.commitIndex = commitIndex  # ?
        # self.term = term
        self.success = True
        self.reply_to = reply_to


class NackMessage(Message):
    def __init__(self, commitIndex, messageId, term, reply_to):
        self.ackMessage = True
        self.messageId = messageId
        self.commitIndex = commitIndex  # ?
        self.term = term
        self.success = False
        self.reply_to = reply_to


# log update
class UpdateMessage(object):
    def __init__(self, term, prevLogIndex, prevLogTerm, entries, leaderCommit, fromLeader):
        self.update = True
        self.requestVote = False
        self.term = term
        self.prevLogIndex = prevLogIndex
        self.prevLogTerm = prevLogTerm
        self.entries = entries
        self.leaderCommit = leaderCommit
        self.fromLeader = fromLeader


# election start
class RequestVoteMessage(object):
    def __init__(self, term, name, lastLogIndex, lastLogTerm):
        self.update = False
        self.requestVote = True
        self.term = term
        self.name = name
        self.lastLogIndex = lastLogIndex
        self.lastLogTerm = lastLogTerm


# election vote
class ElectionVoteMessage(object):
    def __init__(self, term, name, reply_to):
        self.election_vote = True
        self.term = term
        self.name = name
        self.voteGranted = True
        self.reply_to = reply_to
