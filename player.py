from position import Position
from map import Map


class Player:
    current_pos = Position
    start_pos = Position
    id = None
    winner = None
    visited_tiles = None    # list storing tile objects
    past_moves = None       # list storing directions

    def __init__(self, id):
        self.id = id
        self.winner = False
        self.start_pos = generate_rand_pos()
        self.current_pos = Position(self.start_pos)
        self.visited_tiles = []
        self.past_moves = []

    def generate_rand_pos(self):

        size = Map.getMap()
        row = random.randint(0, self.size - 1)
        col = random.randint(0, self.size - 1)
