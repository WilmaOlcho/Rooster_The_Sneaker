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
    
    def get(self, path):
        directory = path.split("/")
        branch = self.sources
        for mkdir in directory:
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
        self.action = "walk"
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
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.enemies = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.sources = source_loader()
        self.sources.create_from_json(json.load(open("mobs.json")))
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

if __name__ == "__main__":
    Game()
    