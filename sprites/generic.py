import pygame
from pygame.sprite import Sprite
from settings import *
from pygame.math import Vector2 as vector
from random import randint, uniform
from player.inventory import Inventory
from support import parse_items_string

class Generic(Sprite):
    def __init__(self, pos, surf, groups, room=None, pos_center=False, draw_secondary=True, player_damage = 0):
        super().__init__(groups)
        self.draw_secondary = draw_secondary
        self.room = room
        if self.room: self.room.dungeon.debug.loaded_entities += 1
        self.debug = None
        if self.room: self.debug = self.room.dungeon.debug
        self.image = surf
        self.player_damage = player_damage
        self.alpha_image = self.image.copy()#; self.alpha_image.set_alpha(SECONDARY_ALPHA)
        if pos_center: self.rect:pygame.Rect = self.image.get_rect(center=pos)
        else: self.rect:pygame.Rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.copy()
        
    def kill(self):
        if self.debug: self.debug.loaded_entities -=1
        super().kill()
        
class Animated(Generic):
    def __init__(self, pos, frames, groups, room=None, pos_center=False,draw_secondary=True,player_damage=0,speed_mul=1):
        self.frames = frames
        self.frame_index = uniform(0.0,0.5)
        self.animation_speed = ANIMATION_SPEED*speed_mul
        super().__init__(pos,self.frames[int(self.frame_index)],groups,room,pos_center,draw_secondary,player_damage)
    
    @runtime
    def animate(self,dt):
        old_frame = int(self.frame_index)
        self.frame_index += self.animation_speed*dt
        if self.frame_index >= len(self.frames): self.frame_index = 0
        if old_frame != int(self.frame_index):
            self.image = self.frames[int(self.frame_index)]
            self.rect = self.image.get_rect(center=self.rect.center)
            self.alpha_image = self.image.copy()#; self.alpha_image.set_alpha(SECONDARY_ALPHA)
    
    @override
    def update(self,dt):
        self.animate(dt)
        self.debug.updates += 1
        
class AnimatedStatus(Animated):
    def __init__(self, pos, animations, status, groups,room=None, pos_center=False,draw_secondary=True,player_damage=0):
        self.animations = animations
        self.status = status
        super().__init__(pos,self.animations[self.status],groups,room,pos_center,draw_secondary,player_damage)
    
    @external
    def set_status(self,status,force=False):
        if self.status != status or force:
            self.status = status; self.frames = self.animations[self.status]
