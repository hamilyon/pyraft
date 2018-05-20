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
        last_known_well = find_log_matches(term, command, log)
        if last_known_well is False:
            return
        log[:] = log[:last_known_well] + self.log

# def find_log_matches(term, command, log):
#     last_known_well = len(log) - 1
#     if last_known_well < 0:
#         return 0
#
#     current_term, current_command = log[last_known_well].term, log[last_known_well].command
#     while (current_term, current_command) != (term, command):
#         last_known_well -= 1
#         if last_known_well < 0:
#             return False
#         current = log[last_known_well]
#         current_term, current_command = current.term, current.command
#     return last_known_well
