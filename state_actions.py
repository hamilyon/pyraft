
class StateUpdate(object):
    """Действие - обновление состояния"""
    def __init__(self, log, commitIndex, lastApplied):
        self.log = log
        self.commitIndex = commitIndex
        self.lastApplied = lastApplied

    def perform(self, socket, state):
        state.append(self.log)
        if self.commitIndex:
            state.commitIndex = self.commitIndex
        if self.lastApplied:
            state.lastApplied = self.lastApplied