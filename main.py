import pygame
from settings import *
from generation.dungeon import Dungeon
from sprites.assetloader import AssetLoader

@singleton
class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode(WINDOW_SIZES,pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        self.asset_loader = AssetLoader()
        self.dungeon_active = True
        self.dungeon = Dungeon(self.asset_loader)
    
    @once
    def run(self):
        first_frame = True
        while True:
            dt = self.clock.tick(FPS)/1000
            
            self.dungeon.run(dt) if self.dungeon_active else None
            if first_frame: self.dungeon.start(); first_frame = False
            
            fps = self.clock.get_fps()
            pygame.display.set_caption(f"{fps=:.2f}")
            pygame.display.update()
        
if __name__ == "__main__":
    main = Main()
    main.run()
