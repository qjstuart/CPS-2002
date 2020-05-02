import enum


class Tile:
    class Status(enum.Enum):
        GRASS = 1
        WATER = 2
        TREASURE = 3

    # HTML representing hidden tile
    element_not_visited = "<img alt=\"Hidden tile\" src=...>"

    def get_status(self):
        return self.Status


class TreasureTile(Tile):
    # HTML representing a treasure tile
    element_treasure_tile = "<img alt=\"Treasure tile\" src=...>"

    def get_html(self, visited):
        if not visited:
            return self.element_not_visited

        return self.element_treasure_tile

    def get_status(self):
        return self.Status.TREASURE.name


class WaterTile(Tile):
    # HTML representing a water tile
    element_water_tile = "<img alt=\"Water tile\" src=...>"

    def get_html(self, visited):
        if not visited:
            return self.element_not_visited

        return self.element_water_tile

    def get_status(self):
        return self.Status.WATER.name


class GrassTile(Tile):
    # HTML representing a grass tile
    element_grass_tile = "<img alt=\"Grass tile\" src=...>"

    def get_html(self, visited):
        if not visited:
            return self.element_not_visited

        return self.element_grass_tile

    def get_status(self):
        return self.Status.GRASS.name
