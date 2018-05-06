import unittest

import zeromq_context
from core import  Raft


class TestProblem(unittest.TestCase):
    def setUp(self):
        context = zeromq_context.context

        self.raft = Raft('test', context)



    def test_sample(self):

        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()

