import pygame
import json
from source_loader import SourceLoader
from maps import Map


class Map_creator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), pygame.FULLSCREEN)
        self.enemies = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.sources = SourceLoader()
        self.sources.create_from_json(json.load(open("tiles.json")))
        self.sources.create_from_json(json.load(open("mobs.json")))
        self.map = EditableMap(self.sources, "map1")
        self.cursor_pos = (0, 0)
        self.display_pos = (0, 0)
        self.cursor = pygame.Cursor()
        self.run()

    def cursor_update(self):
        mouse_pos = pygame.mouse.get_pos()
        dummytile = self.sources.get(self.map.possible_tiles[self.map.possible_tile_index])
        self.cursor_pos = ((mouse_pos[0] + self.display_pos[0])//16, (mouse_pos[1] + self.display_pos[1])//16)
        if mouse_pos[0] > self.screen.get_width() - dummytile.get_width():
            self.display_pos = (self.display_pos[0] + 10, self.display_pos[1])
        if mouse_pos[0] < dummytile.get_width():
            self.display_pos = (self.display_pos[0] - 10, self.display_pos[1])
        if mouse_pos[1] > self.screen.get_height() - dummytile.get_height():
            self.display_pos = (self.display_pos[0], self.display_pos[1] + 10)
        if mouse_pos[1] < dummytile.get_height():
            self.display_pos = (self.display_pos[0], self.display_pos[1] - 10)
        if self.display_pos[0] < 0: self.display_pos = (0, self.display_pos[1])
        if self.display_pos[1] < 0: self.display_pos = (self.display_pos[0], 0)
        if self.display_pos[0] > self.map.width: self.display_pos = (self.map.width, self.display_pos[1])
        if self.display_pos[1] > self.map.height: self.display_pos = (self.display_pos[0], self.map.height)
        
        pygame.draw.rect(self.map.rendered, (255, 255, 255), (self.cursor_pos[0]*16, self.cursor_pos[1]*16, dummytile.get_width(), dummytile.get_height()), 1)
        self.map.rendered.blit(dummytile, (self.cursor_pos[0]*16, self.cursor_pos[1]*16, dummytile.get_width(), dummytile.get_height()))
    
    def draw(self, screen:pygame.Surface):
        screen.fill((0, 0, 0))
        self.cursor_update()
        screen.blit(self.map.rendered, (0, 0), (self.display_pos[0], self.display_pos[1], 800, 600))
        screen.blit(pygame.font.SysFont("Arial",14).render(f'x:{self.cursor_pos[0]}, y:{self.cursor_pos[1]}', False,(255,0,0)), (0, 0))
        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.map.click(self.cursor_pos[0]*16, self.cursor_pos[1]*16)
                if event.type == pygame.MOUSEWHEEL:
                    self.map.scrollwheel(event.y)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return
                    if event.key == pygame.K_s:
                        file = open("maps.json", "w+")
                        try:
                            data = json.load(file)
                        except:
                            data = {}
                        data[self.map.name] = self.map.map
                        json.dump(data, file)
                        file.close()
                    if event.key == pygame.K_r:
                        self.map.create_map()
                    if event.key == pygame.K_d:
                        for tile in self.map.map.get("tiles"):
                            if tile.get("x") == self.cursor_pos[0]*16 + self.display_pos[0] and tile.get("y") == self.cursor_pos[1]*16 + self.display_pos[1]:
                                self.map.map.get("tiles").remove(tile)
                                break
                    

            self.map.update()
            self.draw(self.screen)
            self.clock.tick(60)

class EditableMap(Map):
    def __init__(self, sources:SourceLoader, name):
        self.sources = sources
        self.name = name
        try:
            self.map = json.load(open("maps.json")).get(name, None)
        except:
            self.create_map()
       
        self.width = self.map.get("width")
        self.height = self.map.get("height")
        self.rendered = pygame.Surface((self.width, self.height))

        self.possible_tiles = self.sources.get("environment/*paths")
        self.possible_tile_index = 0

    def create_tiles(self):
        for tile in self.map.get("tiles"):
            x, y = tile.get("x"), tile.get("y")
            image = self.sources.get(tile.get("path"))
            self.rendered.blit(image, (x, y))
        
    def create_map(self):
        file = open("maps.json", "w+")
        self.map = {
            "width": 8000,
            "height": 6000,
            "tiles": []
        }
        try:
            data = json.load(file)
        except:
            data = None
        if data is None:
            data = {}
        data[self.name] = self.map
        json.dump(data, file)
        file.close()

    def update(self):
        self.rendered.fill((0,0,0))
        self.create_tiles()

    def click(self, x, y):
        tile = self.possible_tiles[self.possible_tile_index]
        if self.map.get("tiles") is None:
            self.map["tiles"] = []
        self.map["tiles"].append({
            "x": x,
            "y": y,
            "path": tile
        })

    def scrollwheel(self, direction):
        self.possible_tile_index += direction
        if self.possible_tile_index < 0: self.possible_tile_index = 0
        if self.possible_tile_index >= len(self.possible_tiles): self.possible_tile_index = len(self.possible_tiles) - 1
        
