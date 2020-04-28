import enum


class Tile:
    class Status(enum.Enum):
        grass = 1
        water = 2
        treasure = 3

    # HTML representing hidden tile
    element_not_visited = "<img alt=\"Hidden tile\" src=...>"


class TreasureTile(Tile):
    # HTML representing a treasure tile
    element_treasure_tile = "<img alt=\"Treasure tile\" src=...>"

    def get_html(self, visited):
        if not visited:
            return self.element_not_visited

        return self.element_treasure_tile

    def get_status(self):
        return self.Status.treasure.name


class WaterTile(Tile):
    # HTML representing a water tile
    element_water_tile = "<img alt=\"Water tile\" src=...>"

    def get_html(self, visited):
        if not visited:
            return self.element_not_visited

        return self.element_water_tile

    def get_status(self):
        return self.Status.water.name


class GrassTile(Tile):
    # HTML representing a grass tile
    element_grass_tile = "<img alt=\"Grass tile\" src=...>"

    def get_html(self, visited):
        if not visited:
            return self.element_not_visited

        return self.element_grass_tile

    def get_status(self):
        return self.Status.grass.name
