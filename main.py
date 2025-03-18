from sys import argv

import pygame
from random import randint, choice
from map_editor import Map_creator
from source_loader import SourceLoader
from game.mobs import Enemy
import json
    
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        self.enemies = pygame.sprite.Group()
        self.clock = pygame.time.Clock()
        self.sources = SourceLoader()
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

if __name__ == "__main__":
    if len(argv) == 2:
        if argv[1] == "editor":
            Map_creator()
        elif argv[1] == "game":
            Game()
    else:
        Game()
    