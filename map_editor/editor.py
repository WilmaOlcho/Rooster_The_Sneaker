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
        dummytile = pygame.Surface((16, 16))
        match self.map.mode:
            case "tiles":
                if len(self.map.possible_tiles) > 0:
                    dummytile = self.sources.get(self.map.possible_tiles[self.map.index])
            case "mobs":
                if len(self.map.possible_mobs) > 0:
                    dummytile = self.sources.get(self.map.possible_mobs[self.map.index])
            case "inpenetrable": pygame.draw.rect(dummytile, (255, 0, 0), (0, 0, 16, 16), 1)
            case "teleport":
                if len(self.map.possible_teleports) > 0:
                    dummytile = self.sources.get(self.map.possible_teleports[self.map.index])
                    pygame.draw.rect(dummytile, (0, 255, 0), (0, 0, dummytile.get_width(), dummytile.get_height()), 1)
            case "moveable":
                if len(self.map.possible_moveables) > 0:
                    dummytile = self.sources.get(self.map.possible_moveables[self.map.index])
                    pygame.draw.rect(dummytile, (0, 0, 255), (0, 0, dummytile.get_width(), dummytile.get_height()), 1)
            case "npc":
                if len(self.map.possible_npcs) > 0:
                    dummytile = self.sources.get(self.map.possible_npcs[self.map.index])
                    pygame.draw.rect(dummytile, (255, 255, 0), (0, 0, dummytile.get_width(), dummytile.get_height()), 1)
            case "player":
                if len(self.map.possible_players) > 0:
                    dummytile = self.sources.get(self.map.possible_players[self.map.index])
                    pygame.draw.rect(dummytile, (255, 0, 255), (0, 0, dummytile.get_width(), dummytile.get_height()), 1)
 

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
                    if event.key == pygame.K_1:
                        self.map.mode = "tiles"
                    if event.key == pygame.K_2:
                        self.map.mode = "mobs"
                    if event.key == pygame.K_3:
                        self.map.mode = "inpenetrable"
                    if event.key == pygame.K_4:
                        self.map.mode = "teleport"
                    if event.key == pygame.K_5:
                        self.map.mode = "moveable"
                    if event.key == pygame.K_6:
                        self.map.mode = "npc"
                    if event.key == pygame.K_7:
                        self.map.mode = "player"
                    

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

        self.possible_tiles = self.sources.get("environment/*paths",[])
        self.possible_mobs = self.sources.get("mobs/*paths",[])
        self.possible_moveables = self.sources.get("moveables/*paths",[])
        self.possible_teleports = self.sources.get("teleports/*paths",[])
        self.possible_npcs = self.sources.get("npcs/*paths",[])
        self.possible_players = self.sources.get("players/*paths",[])

        self.player_blocks = ["spawn", "interact", "teleport"]
        self.impenetrable_blocks = ["wall", "door", "chest", "one-way up", "one-way down", "one-way left", "one-way right"]
        self.moveable_blocks = ["chest", "barrel", "crate", "rock", "bush", "tree"]
        self.npc_blocks = ["npc"]

        self.index = 0
        self._mode = "tiles"

    @property
    def mode(self) -> str:
        return self._mode

    @mode.setter
    def mode(self, value:str) -> None: 
        assert value in ["tiles", "mobs", "inpenetrable", "teleport", "moveable", "npc", "player"]
        self._mode = value
        self.index = 0

    def create_tiles(self):
        for tile in self.map.get("tiles"):
            x, y = tile.get("x"), tile.get("y")
            image = self.sources.get(tile.get("path"))
            self.rendered.blit(image, (x, y))
        for mob in self.map.get("mobs"):
            x, y = mob.get("x"), mob.get("y")
            image = self.sources.get(mob.get("path"))
            self.rendered.blit(image, (x, y))
        for impenetrable in self.map.get("inpenetrable"):
            x, y = impenetrable.get("x"), impenetrable.get("y")
            pygame.draw.rect(self.rendered, (255, 0, 0), (x, y, 16, 16), 1)
            text = pygame.font.SysFont("Arial", 14).render("X", False, (255, 0, 0))
            self.rendered.blit(text, (x, y))
        for teleport in self.map.get("teleport"):
            x, y = teleport.get("x"), teleport.get("y")
            image = self.sources.get(teleport.get("path"))
            pygame.draw.rect(self.rendered, (0, 255, 0), (x, y, image.get_width(), image.get_height()), 1)
            text = pygame.font.SysFont("Arial", 14).render("T", False, (0, 255, 0))
            self.rendered.blit(image, (x, y))
            self.rendered.blit(text, (x, y))
        for moveable in self.map.get("moveable"):
            x, y = moveable.get("x"), moveable.get("y")
            image = self.sources.get(moveable.get("path"))
            self.rendered.blit(image, (x, y))
            pygame.draw.rect(self.rendered, (0, 0, 255), (x, y, image.get_width(), image.get_height()), 1)
        for npc in self.map.get("npc"):
            x, y = npc.get("x"), npc.get("y")
            image = self.sources.get(npc.get("path"))
            self.rendered.blit(image, (x, y, image.get_width(),image.get_height()))
            pygame.draw.rect(self.rendered, (255, 255, 0), (x, y, image.get_width(), image.get_height()), 1)
        for player in self.map.get("player"):
            x, y = player.get("x"), player.get("y")
            image = self.sources.get(player.get("path"))
            self.rendered.blit(image, (x, y))
            pygame.draw.rect(self.rendered, (255, 0, 255), (x, y, image.get_width(), image.get_height()), 1)
        

        
    def create_map(self):
        file = open("maps.json", "w+")
        self.map = {
            "width": 8000,
            "height": 6000,
            "tiles": [],
            "mobs": [],
            "inpenetrable": [],
            "teleport": [],
            "moveable": [],
            "npc": [],
            "player": []
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

    def map_add(self,x,y,parameter, path=None):
        if self.map.get(parameter) is None:
            self.map[parameter] = []
        map_object = {
            "x": x,
            "y": y
        }
        if path is not None:
            map_object["path"] = path
        self.map[parameter].append(map_object)

    def click(self, x, y):
        match self.mode:
            case "tiles": self.map_add(x,y,"tiles",self.possible_tiles[self.index])
            case "inpenetrable": self.map_add(x,y,"inpenetrable")
            case "teleport": self.map_add(x,y,"teleport",self.possible_tiles[self.index])
            case "moveable": self.map_add(x,y,"moveable",self.possible_tiles[self.index])
            case "npc": self.map_add(x,y,"npc",self.possible_tiles[self.index])
            case "player": self.map_add(x,y,"player",self.possible_tiles[self.index])
        
    def scrollwheel(self, direction):
        self.index += direction
        max_value = 0
        match self.mode:
            case "tiles": max_value = len(self.possible_tiles)
            case "mobs": max_value = len(self.possible_mobs)
            case "moveable": max_value = len(self.possible_moveables)
            case "teleport": max_value = len(self.possible_teleports)
            case "npc": max_value = len(self.possible_npcs)
            case "player": max_value = len(self.possible_players)
        if self.index < 0: self.index = 0
        if self.index >= max_value: self.index =  max_value - 1
        
