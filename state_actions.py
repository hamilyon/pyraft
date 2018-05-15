class Action(object):
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented

    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))


class StateUpdate(Action):
    """
    Действие - обновление состояния,

    """
    def __init__(self, log=None, commitIndex=None, serverRole=None, term=None, votedFor=None):
        self.log = log
        self.commitIndex = commitIndex
        self.serverRole = serverRole
        self.term = term
        self.votedFor = votedFor

    def perform(self, socket, state):
        state.extend(self.log)
        if self.commitIndex:
            state.commitIndex = self.commitIndex
        if self.serverRole:
            state.serverRole = self.serverRole

