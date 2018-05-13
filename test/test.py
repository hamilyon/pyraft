import unittest

import zeromq_context
from core import  Raft, Command
from models import UpdateMessage
from state_actions import StateUpdate


class TestProblem(unittest.TestCase):
    def setUp(self):
        context = zeromq_context.context

        self.raft = Raft('first')


    def test_simple_follower_update(self):
        self.raft.state.votedFor = 'second'
        actions = self.raft.receive(UpdateMessage(1, 1, 0, [
            Command('1', 1)
        ], None, 'second'))
        self.assertEqual(actions, [StateUpdate([Command('1', 1)], 1)])

if __name__ == '__main__':
    unittest.main()

