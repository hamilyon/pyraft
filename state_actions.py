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
        if self.log:
            self.extend(state.log)

        if self.commitIndex:
            state.commitIndex = self.commitIndex
        if self.serverRole:
            state.serverRole = self.serverRole

    def extend(self, log):
        term, command = self.log[0].term, self.log[0].command
        i = len(log) - 1
        if i < 0:
            last_known_well = 0
        else:
            current_term, current_command = log[i].term, log[i].command
            while (current_term, current_command) != (term, command):
                i -= 1
                if i < 0:
                    return False
                current = log[i]
                current_term, current_command = current.term, current.command
            last_known_well = i
        log[:] = log[:last_known_well] + self.log
