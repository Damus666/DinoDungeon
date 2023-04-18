import pygame
from settings import *
from .generic import *

class Coin(Animated):
    def __init__(self, pos, vel, frames, particle_frames, groups, particle_groups, room):
        super().__init__(pos, frames, groups, room,True,False)
        self.particle_frames = particle_frames
        self.particle_groups = particle_groups
        self.hitbox.inflate_ip(TILE_SIZE//1.5,TILE_SIZE//1.5)
        self.pos = self.rect.center
        self.vel = vector(vel)
        self.dir = 1 if self.vel.x > 0 else -1
        self.dir_start = self.dir
        friction_amount = -60
        self.friction = vector(self.dir*friction_amount,friction_amount)
        self.can_collect = False
    
    @external
    def collect(self):
        particle = FxEffect(self.rect.center,self.particle_frames,self.particle_groups,self.room,1,0.8)
        self.kill()
    
    @runtime
    def move(self, dt):
        self.vel += self.friction*dt
        self.dir = 1 if self.vel.x > 0 else -1
        if self.dir != self.dir_start: self.vel.x = 0; self.friction.x = 0
        if self.vel.y < 0: self.vel.y = 0; self.friction.y = 0
        if abs(self.vel.x) <= 2 and abs(self.vel.y) <= 2: self.can_collect = True
        self.pos += self.vel*dt
        self.rect.center = (round(self.pos.x),round(self.pos.y))
        self.hitbox.center = self.rect.center
    
    @override
    def update(self, dt):
        self.move(dt)
        self.animate(dt)
        self.debug.updates += 3
        
class Spike(Animated):
    def __init__(self, pos, assets, groups, room):
        self.off_image = assets[0]
        self.alpha_image = self.off_image
        self.on_image = assets[-1]
        self.open_frames = assets
        self.close_frames = list(reversed(assets))
        self.frame_len = len(assets)
        self.is_on = False
        
        super().__init__(pos, self.open_frames, groups, room,False,True,SPIKE_DAMAGE)
        self.pos = vector(self.rect.center)
        self.hitbox.inflate_ip(-TILE_SIZE//4,-TILE_SIZE//4)
    
    @override
    def animate(self, dt):
        if self.is_on:
            if self.frame_index < self.frame_len-1:
                self.frame_index += self.animation_speed * dt
                if self.frame_index >= self.frame_len: self.frame_index = self.frame_len-1; self.image = self.on_image
                else: self.image = self.open_frames[int(self.frame_index)]
        else:
            if self.frame_index < self.frame_len-1:
                self.frame_index += self.animation_speed * dt
                if self.frame_index >= self.frame_len: self.frame_index = self.frame_len-1; self.image = self.off_image
                else: self.image = self.close_frames[int(self.frame_index)]
    
    @external
    def is_close(self):
        if not self.is_on: self.is_on = True; self.frame_index = 0
        self.debug.updates += 1
        
    @external
    def is_far(self):
        if self.is_on: self.is_on = False; self.frame_index = 0
        self.debug.updates += 2

class Fountain(Animated):
    def __init__(self, pos, assets, groups, name, col, room):
        side = "basin" if "bottom" in name else "mid"
        anim_names = []
        for i in range(3): anim_names.append(f"wall_fountain_{side}_{col}_anim_f{i}")
        frames = []
        for name in anim_names: frames.append(assets[name])
        super().__init__(pos, frames, groups,room,False,True,0)
        rect = self.rect.copy()
        inflate_amount = 50
        if side == "basin":
            rect.inflate_ip(0,-inflate_amount)
            rect.midtop = self.rect.midtop
            self.hitbox = rect.copy()
            
class FxEffect(Animated):
    def __init__(self, pos, frames, groups,room, loops=1, speed_mul=1):
        self.loops = loops
        self.loop_count = 0
        super().__init__(pos, frames, groups,room, True,speed_mul=speed_mul)
        self.draw_secondary = False
    
    @override
    def animate(self,dt):
        self.frame_index += self.animation_speed*dt
        if self.frame_index >= len(self.frames):
            if self.loop_count < self.loops-1 or self.loops == -1:
                self.frame_index = 0; self.loop_count += 1
            else:
                self.frame_index = 0
                self.kill()
                return
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.rect.center)
        
class StaticFxEffect(Animated):
    def __init__(self, pos, frames, groups, room,speed_mul=1):
        super().__init__(pos, frames, groups, room,True,speed_mul=speed_mul)
