from source_loader import SourceLoader
import pygame
import json

class Map:
    def __init__(self, sources:SourceLoader, name):
        self.sources = sources
        self.name = name
        try:
            self.map = json.load(open("maps.json")).get(name, None)
        except:
            raise FileNotFoundError("maps.json not found")
        self.width = self.map.get("width")
        self.height = self.map.get("height")
        self.rendered = pygame.Surface((self.width, self.height))

    def create_tiles(self):
        for tile in self.map.get("tiles"):
            x, y = tile.get("x"), tile.get("y")
            image = self.sources.get(tile.get("path"))
            self.rendered.blit(image, (x, y))

    def update(self):
        self.rendered.fill((0,0,0))
        self.create_tiles()

    def click(self, x, y):
        pass

    def scrollwheel(self, direction):
        pass
