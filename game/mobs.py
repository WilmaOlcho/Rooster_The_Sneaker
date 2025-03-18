import pygame
from random import randint, choice
from source_loader import SourceLoader

class Mob(pygame.sprite.Sprite):
    def __init__(self, sources:SourceLoader, name, x, y):
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


class Enemy(Mob):
    def __init__(self, sources:SourceLoader, name, x, y):
        super().__init__()
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
        super().update()
        if self.direction == "left": self.x -= self.speed
        if self.direction == "right": self.x += self.speed
        if self.direction == "up": self.y -= self.speed
        if self.direction == "down": self.y += self.speed
        if self.x > 850 or self.x < -50: self.generate()
        if self.y > 650 or self.y < -50: self.generate()
        self.rect.x = self.x
        self.rect.y = self.y