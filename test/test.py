import unittest

from core import Raft, Command
from models import UpdateMessage, RequestVoteMessage
from state_actions import StateUpdate
from zmq_actions import Ack, Nack, ElectionVote


class TestRaft(unittest.TestCase):
    def setUp(self):
        self.raft = Raft('first')

    def test_simple_follower_update(self):
        self.raft.state.votedFor = 'second'
        message = UpdateMessage(
            term=1,
            prevLogIndex=0,
            prevLogTerm=0,
            entries=[Command('1', 1)],
            leaderCommit=1,
            fromLeader='second'
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [Ack(term=1, reply_to=message), StateUpdate([Command('1', term=1)], commitIndex=1, term=1)])

    def test_new_term_follower_update(self):
        self.raft.state.votedFor = 'second'
        message = UpdateMessage(
            term=2,
            prevLogIndex=0,
            prevLogTerm=0,
            entries=[Command('1', 1)],
            leaderCommit=1,
            fromLeader='second'
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [Ack(term=2, reply_to=message), StateUpdate([Command('1', term=1)], commitIndex=1, term=2)])

    def test_old_term_follower_ignore(self):
        self.raft.state.votedFor = 'second'
        self.raft.state.term = 1
        message = UpdateMessage(
            term=0,
            prevLogIndex=0,
            prevLogTerm=0,
            entries=[Command('1', 1)],
            leaderCommit=1,
            fromLeader='second'
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [Nack(term=1, reply_to=message)])


    def test_follower_votes(self):
        self.raft.state.votedFor = 'second'
        self.raft.state.term = 0
        message = RequestVoteMessage(
            term=1,
            name='third',
            lastLogIndex=1,
            lastLogTerm=0,
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [
            ElectionVote(name='third', term=1, reply_to=message),
            StateUpdate(votedFor='third', term=1)
        ])

    def test_follower_no_log_vote(self):
        self.raft.state.votedFor = 'second'
        self.raft.state.term = 0
        message = RequestVoteMessage(
            term=1,
            name='third',
            lastLogIndex=-1,
            lastLogTerm=-1,
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [
            ElectionVote(name='third', term=1, reply_to=message),
            StateUpdate(votedFor='third', term=1)
        ])

    def test_follower_match_log_vote(self):
        self.raft.state.votedFor = 'second'
        self.raft.state.term = 0
        self.raft.state.log = [Command('1', term=1)]
        message = RequestVoteMessage(
            term=1,
            name='third',
            lastLogIndex=0,
            lastLogTerm=1,
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [
            ElectionVote(name='third', term=1, reply_to=message),
            StateUpdate(votedFor='third', term=1)
        ])

    def test_follower_ignores_stale_elections(self):
        self.raft.state.votedFor = 'second'
        self.raft.state.term = 1
        message = RequestVoteMessage(
            term=1,
            name='third',
            lastLogIndex=1,
            lastLogTerm=0,
        )
        actions = self.raft.receive(message)
        self.assertEqual(actions, [])


if __name__ == '__main__':
    unittest.main()
