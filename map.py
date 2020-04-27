class Map:
    size = 0

    # def __init__(self, size):`
    #     self.size = size

    # def generate():

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
            print("Size: ", self.size)
            return True


    # def generate():


class Tile:
    type = ["treasure", "water", "grass"]
