import unittest
from map import Map


class TestSetMapSize(unittest.TestCase):
    def test_boolean_output(self):

        # Test map of size >= 0 for 0 players
        m1 = Map()
        self.assertFalse(m1.set_map_size(0, 0))
        self.assertFalse(m1.set_map_size(5, 0))
        self.assertFalse(m1.set_map_size(8, 0))
        self.assertFalse(m1.set_map_size(51, 0))

        # Test map of size 0 for >= 0 players
        self.assertFalse(m1.set_map_size(0, 0))
        self.assertFalse(m1.set_map_size(0, 2))
        self.assertFalse(m1.set_map_size(0, 8))
        self.assertFalse(m1.set_map_size(0, 9))

        # Test map of size 5x5 - 50x50 for 2-8 players
        self.assertTrue(m1.set_map_size(5, 2))
        self.assertTrue(m1.set_map_size(8, 4))
        self.assertTrue(m1.set_map_size(35, 6))
        self.assertTrue(m1.set_map_size(50, 8))

    def test_values(self):

        m1 = Map()
        # Ensure type errors are raised when necessary
        self.assertRaises(TypeError, m1.set_map_size, 'hello', 'hi')
        self.assertRaises(TypeError, m1.set_map_size, 3j, 3j)

        # Test negative map size and number of players
        self.assertRaises(ValueError, m1.set_map_size, -5, 2)
        self.assertRaises(ValueError, m1.set_map_size, 5, -2)


