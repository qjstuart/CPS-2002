from position import Position
from map import Map
import random


class Player:
    current_pos = Position
    start_pos = Position
    id = None
    winner = None
    visited_tiles = None    # list storing tile objects
    past_moves = None       # list storing directions

    def __init__(self, identity):
        self.id = identity
        self.winner = False
        self.visited_tiles = []
        self.past_moves = []

    def generate_rand_pos(self):

        size = Map.get_instance().get_map_size
        row = random.randint(0, size - 1)
        col = random.randint(0, size - 1)
        return Position(row, col)