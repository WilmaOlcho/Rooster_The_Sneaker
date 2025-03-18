import pygame

class SourceLoader:
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