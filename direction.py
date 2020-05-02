import enum


class Direction:
    class Direction(enum.Enum):
        up = 'u'
        down = 'd'
        left = 'l'
        right = 'r'

    direction = None

    def __init__(self, character):
        self.direction = character

    def get_direction(self):
        return self.direction


