import pygame
from random import randint, choice

class source_loader:
    def __init__(self):
        self.sources = {}

    def load_assets(self, assets_branch:dict):
        for action in assets_branch.values():
            if action.get("spritesheet", None):
                self.load_spritesheet(action)
            if action.get("sounds", None):
                self.load_sounds(action)

    def create_from_json(self, json_data:dict):
        for value in json_data.values():
            if value.get("assets", None):
                self.load_assets(value.get("assets"))

    def load_spritesheet(self, json_data:dict):
        from_file = json_data.get("spritesheet", None)
        sprites = json_data.get("sprites", None)
        image = pygame.image.load(from_file).convert_alpha()
        for sprite in sprites:
            x, y, w, h = sprite.get("x"), sprite.get("y"), sprite.get("w"), sprite.get("h")
            path = sprite.get("path")
            self.load(path, image.subsurface(pygame.Rect(x, y, w, h)))        

    def load_sounds(self, json_data:dict):
        for sound in json_data.get("sounds", None):
            path = sound.get("path")
            self.load(path, pygame.mixer.Sound(path))

    def load(self, path, source, branch:dict=None):
        current_branch = self.sources if branch is None else branch
        directory = path.split("/")
        if directory[0] != '':
            if directory[0] not in current_branch.keys():
                current_branch[directory[0]] = {}
        if len(directory) == 1:
            current_branch[directory[0]] = source
            return current_branch.get(directory[0], None)
        current_branch = current_branch[directory[0]]
        return self.load("/".join(directory[1:]),source, branch=current_branch)
    
    def get_all_paths(self, branch, path=""):
        all_paths = []
        for key, value in branch.items():
            if isinstance(value, dict):
                all_paths.extend(self.get_all_paths(value, path+key+"/"))
            else:
                all_paths.append(path+key)
        return all_paths

    def get(self, path):
        directory = path.split("/")
        branch = self.sources
        for mkdir in directory:
            if mkdir == "*paths":
                return list(self.get_all_paths(branch, "/".join(directory[:-1])+"/"))
            branch = branch.get(mkdir, None)
            if not branch: break
        return branch
    

class Enemy(pygame.sprite.Sprite):
    def __init__(self, sources:source_loader, name, x, y):
        super().__init__()
        self.sources = sources
        self.name = name
        self.w = 64
        self.h = 64
        self.x = float(x)
        self.y = float(y)

        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.frame = 0
        self.action = choice(["idle", "walk", "attack", "hurt", "death", "run"])
        self.direction = "right"

        self.mob_class = self.name.lower()[:-1]
        self.mob_type = self.name.lower()[-1]

        self.chunk = self.sources.get(f"mobs/{self.mob_class}/{self.mob_type}/{self.action}/{self.direction}/{self.frame}")
        self.image = pygame.transform.scale(self.chunk, (50, 50))
        self.rect = self.image.get_rect()

        self.speed = randint(1, 10)/10

    def generate(self):
        self.direction = choice(["left", "right", "up", "down"])
        if self.direction == "left":
            self.x = 850
            self.y = randint(0, 550)
        if self.direction == "right":
            self.x = -50
            self.y = randint(0, 550)
        if self.direction == "up":
            self.x = randint(0, 750)
            self.y = 650
        if self.direction == "down":
            self.x = randint(0, 750)
            self.y = -50
        self.speed = randint(1, 10)/10

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            while True:
                self.chunk = self.sources.get(f"mobs/{self.mob_class}/{self.mob_type}/{self.action}/{self.direction}/{self.frame}")
                if self.chunk:
                    break
                self.frame = 0
            self.image = pygame.transform.scale(self.chunk, (50, 50))
        if self.direction == "left": self.x -= self.speed
        if self.direction == "right": self.x += self.speed
        if self.direction == "up": self.y -= self.speed
        if self.direction == "down": self.y += self.speed
        if self.x > 850 or self.x < -50: self.generate()
        if self.y > 650 or self.y < -50: self.generate()
        self.rect.x = self.x
        self.rect.y = self.y
import json



class Map:
    def __init__(self, sources:source_loader, name):
        self.sources = sources
        self.name = name
        try:
            self.map = json.load(open("maps.json")).get(name, None)
        except:
            self.map = None
        if self.map is None:
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
        

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.enemies = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.sources = source_loader()
        self.sources.create_from_json(json.load(open("mobs.json")))
        self.sources.create_from_json(json.load(open("tiles.json")))
        for i in range(100):
            name = choice(["Slime1", "Slime2", "Slime3"])
            enemy = Enemy(self.sources, name, randint(0, 750), randint(0, 600))
            enemy.direction = choice(["left", "right", "up", "down"])
            self.enemies.add(enemy)
        self.run()
        
    def update(self):
        self.enemies.update()

    def draw(self, screen):
        screen.fill((0, 0, 0))
        self.enemies.draw(screen)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            self.update()
            self.draw(self.screen)
            pygame.display.flip()
            self.clock.tick(60)

class Map_creator:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.enemies = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.sources = source_loader()
        self.sources.create_from_json(json.load(open("tiles.json")))
        self.sources.create_from_json(json.load(open("mobs.json")))
        self.map = Map(self.sources, "map1")
        self.cursor_pos = (0, 0)
        self.display_pos = (0, 0)
        self.cursor = pygame.Cursor()
        self.run()

    def draw(self, screen:pygame.Surface):
        screen.fill((0, 0, 0))
        mouse_pos = pygame.mouse.get_pos()
        self.cursor_pos = ((mouse_pos[0] + self.display_pos[0])//16, (mouse_pos[1] + self.display_pos[1])//16)
        if mouse_pos[0] > 750:
            self.display_pos = (self.display_pos[0] + 16, self.display_pos[1])
        if mouse_pos[0] < 50:
            self.display_pos = (self.display_pos[0] - 16, self.display_pos[1])
        if mouse_pos[1] > 550:
            self.display_pos = (self.display_pos[0], self.display_pos[1] + 16)
        if mouse_pos[1] < 50:
            self.display_pos = (self.display_pos[0], self.display_pos[1] - 16)
        if self.display_pos[0] < 0: self.display_pos = (0, self.display_pos[1])
        if self.display_pos[1] < 0: self.display_pos = (self.display_pos[0], 0)
        if self.display_pos[0] > 8000: self.display_pos = (8000, self.display_pos[1])
        if self.display_pos[1] > 6000: self.display_pos = (self.display_pos[0], 6000)
        pygame.draw.rect(self.map.rendered, (255, 255, 255), (self.cursor_pos[0]*16, self.cursor_pos[1]*16, 16, 16), 1)
        dummytile = self.sources.get(self.map.possible_tiles[self.map.possible_tile_index])
        self.map.rendered.blit(dummytile, (self.cursor_pos[0]*16, self.cursor_pos[1]*16, dummytile.get_width(), dummytile.get_height()))
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
                        self.map.click(self.cursor_pos[0]*16 + self.display_pos[0], self.cursor_pos[1]*16 + self.display_pos[1])
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

if __name__ == "__main__":
    #Game()
    Map_creator()
    