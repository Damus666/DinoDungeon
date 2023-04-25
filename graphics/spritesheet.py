import pygame
from settings import *

@helper

class SingleSpritesheet:
    def __init__(self, surface:pygame.Surface):
        self.sheet = surface
        self.size = self.sheet.get_height()
        self.len = self.sheet.get_width()//self.size
    
    @once
    def frames(self): return [self.sheet.subsurface((i*self.size,0,self.size,self.size)) for i in range(self.len)]
    
class Spritesheet:
    def __init__(self, surface:pygame.Surface, size:int):
        self.sheet = surface
        self.size = size
        self.len_w,self.len_h = self.sheet.get_width()//self.size,self.sheet.get_height()//self.size
        
    @once
    def frames(self,scale=1):
        return [pygame.transform.scale_by(self.sheet.subsurface((self.size*col,self.size*row,self.size,self.size)),scale) \
            for row in range(self.len_h) for col in range(self.len_w)]
    
    @once
    def frames_grid(self,scale=1):
        return [[pygame.transform.scale_by(self.sheet.subsurface((self.size*col,self.size*row_i,self.size,self.size)),scale) \
            for col in range(self.len_w)] for row_i in range(self.len_h) ]
