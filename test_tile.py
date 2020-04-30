import unittest
from map import Map
from tile import Tile, TreasureTile, GrassTile, WaterTile


class TestSetMapSize(unittest.TestCase):
    def test_object_types(self):
        m1 = Map()
        t1 = TreasureTile()
        t2 = WaterTile()
        t3 = GrassTile()

        # Ensure that instantiated variables are of correct object type
        self.assertIsInstance(m1, Map)
        self.assertIsInstance(t1, TreasureTile)
        self.assertIsInstance(t2, WaterTile)
        self.assertIsInstance(t3, GrassTile)

        # Ensuring treasure, water and grass tile correctly inherit from Tile class
        self.assertIsInstance(t1, Tile)
        self.assertIsInstance(t2, Tile)
        self.assertIsInstance(t3, Tile)