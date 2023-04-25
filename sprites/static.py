import pygame
from settings import *
from .generic import *
from .animated import FxEffect
        
class Drop(Generic):
    def __init__(self,pos,vel,surf,name,groups,particle_frames,particle_groups,room):
        w,h = surf.get_size(); scale = DROP_SCALE
        super().__init__(pos,pygame.transform.scale(surf,(int(w*scale),int(h*scale))),groups,room,True)
        self.name = name
        self.particle_frames = particle_frames
        self.particle_groups = particle_groups
        self.pos = vector(self.rect.center)
        self.vel = vector(vel)
        self.dir = 1 if self.vel.x > 0 else -1
        self.dir_start = self.dir
        friction_amount = -60
        self.friction = vector(self.dir*friction_amount,friction_amount)
        self.can_collect = False
        self.static_y = self.rect.centery
        self.idle_dir = 1
        self.idle_offset = 0
        self.max_y,self.min_y = self.static_y+DROP_IDLE_OFFSET,self.static_y-DROP_IDLE_OFFSET
    
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
        if abs(self.vel.x) <= 2 and abs(self.vel.y) <= 2:
            self.can_collect = True
            self.rect.center = (round(self.pos.x),round(self.pos.y))
            self.hitbox.center = self.rect.center
            self.static_y = self.rect.centery
            self.max_y,self.min_y = self.static_y+DROP_IDLE_OFFSET,self.static_y-DROP_IDLE_OFFSET
        self.pos += self.vel*dt
        if not self.can_collect:
            self.rect.center = (round(self.pos.x),round(self.pos.y))
            self.hitbox.center = self.rect.center
        else:
            self.idle_offset += DROP_IDLE_SPEED*self.idle_dir*dt
            self.rect.centery = self.static_y+self.idle_offset
            if self.rect.centery >= self.max_y or self.rect.centery <= self.min_y: self.idle_dir *= -1
        
    @override
    def update(self, dt):
        self.move(dt)
        self.debug.updates += 2
        
class Skull(Generic):
    def __init__(self, pos, surf, groups, room):
        super().__init__(pos, surf, groups, room,False)
        
        if randint(0,100) <= 50: self.image = pygame.transform.flip(self.image,True,False)
        
        offset = vector(randint(-20,20),randint(-20,20))
        self.rect.center = (self.rect.centerx+offset.x,self.rect.centery+offset.y)
        
class Wall(Generic):
    def __init__(self, pos, surf, groups, room,name):
        super().__init__(pos, surf, groups, room)
        rect = self.rect.copy()
        inflate_amount = 50
        if "top" in name and "corner" in name:
            rect.inflate_ip(-inflate_amount,-inflate_amount)
            if "right" in name: rect.bottomleft = self.rect.bottomleft
            elif "left" in name: rect.bottomright = self.rect.bottomright
        elif "top" in name:
            rect.inflate_ip(0,-inflate_amount); rect.midbottom = self.rect.midbottom
        elif "column_bottom" in name or "goo" in name or "fountain_bottom" in name:
            rect.inflate_ip(0,-inflate_amount); rect.midtop = self.rect.midtop
        self.hitbox = rect.copy()
        
class Collider(Generic):
    def __init__(self, pos, size, group, room):
        super().__init__(pos,pygame.Surface(size),group,room,False)
        
class InventoryInfoMsg(Generic):
    def __init__(self, pos, message, font, drop, groups, room):
        self.font = font
        self.message = message
        self.drop = drop
        surf = self.font.render(message,False,"red")
        self.alpha = 255
        self.can_disappear = False
        self.born_time = pygame.time.get_ticks()
        self.cooldown = 0.8*1000
        super().__init__(pos,surf,groups,room,True)
        
    def update(self, dt):
        if self.can_disappear:
            self.alpha -= MSG_DISAPPEAR_SPEED * dt
            if self.alpha <= 0: self.kill()
            else: self.image.set_alpha(int(self.alpha))
        else:
            if pygame.time.get_ticks() - self.born_time >= self.cooldown: self.can_disappear = True
        self.debug.updates += 1

class FloatingUI(pygame.sprite.Sprite):
    def __init__(self, end_rect, image, debug, center=False):
        super().__init__()
        self.debug = debug
        self.debug.loaded_entities += 1
        
        self.center = center
        self.image = image
        self.rect = self.image.get_rect(center=(H_WIDTH,H_HEIGHT+TILE_SIZE))
        self.end_rect = end_rect
        self.pos = vector(self.rect.center)
        self.speed = UI_COIN_SPEED
        self.dir = vector(1,1)*50
        self.target_dir = (vector(self.end_rect.bottomright)-vector(H_WIDTH,H_HEIGHT)).normalize()
        
    def update(self, dt):
        self.target_dir = (vector(self.end_rect.bottomright if not self.center else self.end_rect.center)-self.pos)
        if self.target_dir.magnitude() != 0: self.target_dir.normalize_ip()
        self.dir += self.target_dir*2
        self.pos += self.dir*self.speed*dt
        self.rect.center = (round(self.pos.x),round(self.pos.y))
        if self.rect.colliderect(self.end_rect) or self.rect.right < 0 or self.rect.top < 0: self.kill(); self.debug.loaded_entities -= 1
        self.debug.updates += 1
            
class Disappearing(Generic):
    def __init__(self, pos, surf, groups, room,cooldown, disappear_callback,pos_center=False, draw_secondary=True, player_damage=0):
        super().__init__(pos,surf,groups,room,pos_center,draw_secondary,player_damage)
        self.born_time = pygame.time.get_ticks()
        self.cooldown = cooldown
        self.disappear_callback = disappear_callback
        
    def update(self, dt):
        if pygame.time.get_ticks()-self.born_time >= self.cooldown:
            self.kill()
            if self.disappear_callback: self.disappear_callback()
            
class DisappearFaded(Disappearing):
    def __init__(self,pos, surf, groups, room, cooldown, disappear_callback, fade_speed, pos_center=False, draw_secondary=True, player_damage=0, start_full=False):
        super().__init__(pos,surf,groups,room,cooldown,disappear_callback,pos_center,draw_secondary,player_damage)
        self.fade_speed = fade_speed
        self.alpha = 0 if not start_full else 255
        self.direction = 1
        
    def update(self, dt):
        if self.alpha < 255 and self.direction == 1:
            self.alpha += self.fade_speed*dt
            if self.alpha >= 255:
                self.alpha = 255
                self.born_time = pygame.time.get_ticks()
                self.direction = -1
        else:
            if pygame.time.get_ticks()-self.born_time>= self.cooldown:
                self.alpha -= self.fade_speed*dt
                if self.alpha <= 0:
                    self.alpha = 0
                    if self.disappear_callback: self.disappear_callback()
                    self.kill()
        self.image.set_alpha(self.alpha)
        
class WarningMsg(DisappearFaded):
    def __init__(self, pos, surf, groups, room):
        super().__init__(pos,surf,groups,room,900,None,120,True,False,0,True)
