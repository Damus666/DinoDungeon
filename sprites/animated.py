import pygame, math
from settings import *
from .generic import Animated

class Coin(Animated):
    def __init__(self, pos, vel, frames, particle_frames, groups, particle_groups, room, amount=1):
        super().__init__(pos, frames, groups, room,True,False)
        self.particle_frames = particle_frames
        self.particle_groups = particle_groups
        self.amount = amount
        if self.amount > 1: self.frames = [pygame.transform.scale_by(frame,1.8) for frame in self.frames]
        self.hitbox.inflate_ip(TILE_SIZE,TILE_SIZE)
        self.pos = self.rect.center
        self.vel = vector(vel)
        self.dir = 1 if self.vel.x > 0 else -1
        self.dir_start = self.dir
        friction_amount = -60
        self.friction = vector(self.dir*friction_amount,friction_amount)
        self.can_collect = False
    
    @external
    def collect(self):
        FxEffect(self.rect.center,self.particle_frames,self.particle_groups,self.room,1,0.8)
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
        self.debug.updates += 1
        
class Spike(Animated):
    def __init__(self, pos, assets, groups, room):
        self.off_image = assets[0]
        self.alpha_image = self.off_image
        self.on_image = assets[-1]
        self.open_frames = assets
        self.close_frames = list(reversed(assets))
        self.frame_len = len(assets)
        self.is_on = False
        self.last_hit = pygame.time.get_ticks()
        self.hit_cooldown = 3000
        
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
        if pygame.time.get_ticks() - self.last_hit <= self.hit_cooldown: self.is_on = False; return
        if not self.is_on: self.is_on = True; self.frame_index = 0
        self.debug.updates += 1
        
    @external
    def is_far(self):
        if self.is_on: self.is_on = False; self.frame_index = 0
        self.debug.updates += 1
        
    @external
    def damaged(self):
        self.is_far()
        self.last_hit = pygame.time.get_ticks()

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
        self.loops, self.loop_count = loops, 0
        super().__init__(pos, frames, groups,room, True,speed_mul=speed_mul)
        self.draw_secondary, self.finished = False, False
    
    @override
    def animate(self,dt):
        self.frame_index += self.animation_speed*dt
        if self.frame_index >= len(self.frames):
            if self.loop_count < self.loops-1 or self.loops == -1: self.frame_index = 0; self.loop_count += 1
            else:
                self.frame_index, self.finished = 0, True
                self.kill()
                return
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.rect.center)

class FlippedFx(FxEffect):
    def __init__(self, pos, frames, groups, room, flip = True,loops=1, speed_mul = 1):
        super().__init__(pos,frames,groups,room,loops,speed_mul)
        if flip: self.frames = [pygame.transform.flip(frame,True,False) for frame in self.frames]
   
class StaticFxEffect(Animated):
    def __init__(self, pos, frames, groups, room,speed_mul=1):
        super().__init__(pos, frames, groups, room,True,speed_mul=speed_mul)

class Fireball(StaticFxEffect):
    def __init__(self, pos, frames, groups, room, direction, damage=2, speed_mul=1):
        super().__init__(pos,frames,groups,room,1)
        
        self.direction = direction
        self.speed = 500*speed_mul
        self.player_damage = damage
        self.hitbox_size = self.frames[0].get_height()//4
        self.hitbox = pygame.Rect((0,0),(self.hitbox_size,self.hitbox_size))
        angle = math.degrees(math.atan2(-self.direction.y,self.direction.x))
        self.frames = [pygame.transform.rotate(frame, angle) for frame in frames]
        self.pos = vector(self.rect.center)
        self.born_time = pygame.time.get_ticks()
        self.lifetime = 8000
        
    def update(self, dt):
        self.animate(dt)
        self.pos += self.direction*self.speed*dt
        self.rect.center = (round(self.pos.x),round(self.pos.y))
        self.hitbox.center = self.rect.center
        if pygame.time.get_ticks()-self.born_time >= self.lifetime:self.kill()
        