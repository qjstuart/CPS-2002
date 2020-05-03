import unittest
from player import *


class TestPlayerCreation(unittest.TestCase):
    def test_object_types(self):
        p1 = Player('1')
        self.assertIsInstance(p1, Player)
        self.assertEqual(p1.id, '1')


