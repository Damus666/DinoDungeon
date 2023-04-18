from sprites.super import Character
from settings import *
from pygame.math import Vector2 as vector
import pygame

class Enemy(Character):
    def __init__(self, pos, animations, groups, name, font, room):
        super().__init__(pos,animations,groups,room)
        self.name = name
        self.data = self.room.dungeon.map_script.ENEMY_DATA[name]
        self.drop_name, self.special_actions, self.max_health, self.behaviour, self.speed = self.data
        self.special_actions = self.special_actions.split(",")
        self.health = self.max_health
        self.font = font
        
    def damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()
            
    def die(self):
        self.room.defeated(self)
        self.kill()
        
    def draw_name(self, screen, offset):
        pass

    def update(self, dt):
        self.animate(dt)
        self.debug.updates += 2
        
class EnemyAttacker(Enemy):
    def __init__(self,pos,animations,groups,name,font,room, vision_range=ENEMY_VISION_RANGE):
        super().__init__(pos,animations,groups,name,font,room)
        self.vision_range = vision_range
        self.collidable = self.room.collidable
        self.is_chasing = False
        self.orientation = "right"
        self.direction:vector = vector()
        self.hitbox = self.rect.inflate(-self.rect.w/4,0)
        self.hitbox.h = TILE_SIZE//4
        self.can_chase = self.behaviour=="attack"
        self.original_animations = self.animations
        self.flipped_animations = {
            key: [pygame.transform.flip(sprite,True,False) for sprite in value]
            for key, value in self.animations.items()
        }
        
    def chase(self,dt):
        if self.pos.distance_to(self.player.pos) <= self.vision_range and self.can_chase: self.is_chasing = True
        else: self.is_chasing = False
        if self.is_chasing:
            self.direction:vector = self.player.pos-self.pos
            if self.direction.x > 0: self.orientation = "right"
            else: self.orientation = "left"
            if self.direction.magnitude() != 0: self.direction.normalize_ip()
            
            self.pos.x += self.direction.x*self.speed*dt
            self.rect.centerx = round(self.pos.x)
            self.hitbox.midbottom = self.rect.midbottom
            self.collisions("horizontal")
            self.pos.y += self.direction.y*self.speed*dt
            self.rect.centery = round(self.pos.y)
            self.hitbox.midbottom = self.rect.midbottom
            self.collisions("vertical")
        elif self.direction.x != 0 or self.direction.y != 0: self.direction = vector()
            
    def collisions(self, direction):
        for sprite in self.collidable:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == "horizontal":
                    self.hitbox.right = sprite.hitbox.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.hitbox.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                    self.direction.x = 0
                else:
                    self.hitbox.top = sprite.hitbox.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.hitbox.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.bottom = self.hitbox.bottom
                    self.pos.y = self.rect.centery
                    self.direction.y = 0
                    
    def get_status(self):
        status = "idle"
        if self.direction.x != 0 or self.direction.y != 0: status = "run"
        if self.orientation == "left": self.animations = self.flipped_animations
        else: self.animations = self.original_animations
        self.set_status(status, True)
        
    def update(self, dt):
        self.get_status()
        self.animate(dt)
        self.chase(dt)
        self.debug.updates += 4

class Boss(EnemyAttacker):
    def __init__(self, pos, animations, groups, name, font, room):
        super().__init__(pos,animations,groups,name,font,room,BOSS_VISION_RANGE)
        