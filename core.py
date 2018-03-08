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

        return actions

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
