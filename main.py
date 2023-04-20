import pygame
from settings import *
from generation.dungeon import Dungeon
from graphics.assetloader import AssetLoader
from generation.maploader import MapLoader

@singleton
class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode(WINDOW_SIZES,pygame.FULLSCREEN)
        pygame.display.set_caption("Dino Dungeon")
        self.clock = pygame.time.Clock()
        self.asset_loader = AssetLoader()
        self.dungeon_active = True
        self.maps = {name:MapLoader(name) for name in MAP_NAMES}
        self.dungeon = Dungeon(self.asset_loader,self.clock, self.maps, "DungeonFeatures")
    
    @once
    def run(self):
        first_frame = True
        while True:
            dt = self.clock.tick(FPS)/1000
            
            self.dungeon.run(dt) if self.dungeon_active else None
            if first_frame: self.dungeon.start(); first_frame = False
            
            pygame.display.update()
        
if __name__ == "__main__":
    main = Main()
    main.run()
