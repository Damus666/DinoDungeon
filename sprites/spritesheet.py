import pygame
from settings import *

@helper
class SingleSpriteSheet:
    def __init__(self, surface:pygame.Surface):
        self.sheet = surface
        self.size = self.sheet.get_height()
        self.len = self.sheet.get_width()//self.size
    
    @once
    def frames(self):
        frames = []
        for i in range(self.len):
            surf = self.sheet.subsurface((i*self.size,0,self.size,self.size))
            frames.append(surf)
        return frames

