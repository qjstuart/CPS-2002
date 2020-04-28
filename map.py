import tile
import math
import random


class Map:
    size = None
    tiles = [], []

    def reset_map(self):
        self.size = 0
        self.tiles = None
        return self

    def set_map_size(self, x, n):

        if (type(x) or type(n)) not in [int]:
            raise TypeError("Map size and number of players must be a non-negative real number.")

        if x < 0 or n < 0:
            raise ValueError("Map size and number of players cannot be negative.")

        if x > 50 or n < 2 or n > 8:
            return False

        if n >= 2 and x < 5:
            return False

        if n >= 5 and x < 8:
            return False

        else:
            self.size = x
            return True

    def generate_map(self):

        if self.size < 5 or self.size > 50:
            raise Exception("Map size cannot be smaller than 5x5 or larger than 50x50.")

        tiles = [self.size][self.size]

    def generate_water_tiles(self):

        total_tiles = self.size * self.size
        total_water_tiles = math.floor(0.2 * total_tiles)

        # Populate 2D array with tile types
        i = 1
        while i < total_water_tiles:

            row = random.randint(1, self.size)
            col = random.randint(1, self.size)

            ''' 
            If there is no tile in randomly selected coordinate,
            place a Water Tile at that coordinate.
            '''

            if self.tiles[row][col] is None:
                self.tiles[row][col] = tile.WaterTile()
                i += 1

    def generate_treasure_tile(self):

        row = random.randint(1, self.size)
        col = random.randint(1, self.size)

        if self.tiles[row][col] is None:
            self.tiles[row][col] = tile.TreasureTile()

        else:
            self.generate_treasure_tile()

    def generate_grass_tile(self):
        for i in self.size:
            for j in self.size:
                if self.tiles[i][j] is None:
                    self.tiles[i][j] = tile.GrassTile()
