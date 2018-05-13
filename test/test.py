import unittest

from core import Raft, Command
from models import UpdateMessage
from state_actions import StateUpdate
from zmq_actions import Ack


class TestRaft(unittest.TestCase):
    def setUp(self):
        self.raft = Raft('first')

    def test_simple_follower_update(self):
        self.raft.state.votedFor = 'second'
        message = UpdateMessage(1, 1, 0, [Command('1', 1)], 1, 'second')
        actions = self.raft.receive(message)
        self.assertEqual(actions, [Ack(1, message), StateUpdate([Command('1', 1)], 1)])


if __name__ == '__main__':
    unittest.main()
