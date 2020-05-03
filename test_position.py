import unittest
from position import *


class TestPositionObject(unittest.TestCase):
    def test_object_creation(self):
        p1 = Position(5, 7)
        self.assertIsInstance(p1, Position)
        self.assertEqual(p1.row, 5)
        self.assertEqual(p1.col, 7)


