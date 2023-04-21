from sprites.super import Character
from sprites.animated import FxEffect, Fireball
from sprites.static import WarningMsg
from settings import *
from support import *
from pygame.math import Vector2 as vector
import pygame

class Enemy(Character):
    def __init__(self, pos, animations, groups, name, font, room):
        super().__init__(pos,animations,groups,room)
        self.name = name
        self.data = self.room.dungeon.map_script.ENEMY_DATA[name]
        self.drop_names, self.special_actions, self.max_health, self.behaviour, self.speed, self.attack_data = self.data
        self.special_actions = self.special_actions.split(",")
        self.health = self.max_health
        self.font = font
        self.attack_mode = 0
        self.cramming_rect = self.rect
        
        self.last_damage = 0
        self.hit_cooldown = 1000
            
    @external
    def damage(self, amount):
        if pygame.time.get_ticks() - self.last_damage >= self.hit_cooldown:
            self.health -= amount
            if self.health <= 0:
                self.die()
            self.last_damage = pygame.time.get_ticks()

    def die(self):
        for name in self.drop_names:
            item = item_from_name(name)
            self.room.drop_item(item,self.rect.center)
        self.room.defeated(self)
        self.kill()
    
    @runtime
    def draw_name(self, screen, offset): pass
    def draw_extra(self,screen,offset): pass

    @override
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
    
    @runtime
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

    @runtime
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
    
    @runtime         
    def get_status(self):
        status = "idle"
        if self.direction.x != 0 or self.direction.y != 0: status = "run"
        if self.orientation == "left": self.animations = self.flipped_animations
        else: self.animations = self.original_animations
        self.set_status(status, True)
    
    @override
    def update(self, dt):
        self.get_status()
        self.animate(dt)
        self.chase(dt)
        self.extra_update(dt)
        self.debug.updates += 3
    @runtime
    def extra_update(self, dt):pass
    
class SmallEnemy(EnemyAttacker):
    def __init__(self,pos,animations,groups,name,font,room):
        super().__init__(pos,animations,groups,name,font,room)
        self.other_enemies = room.enemies
        self.player = room.player
        self.size = (self.rect.w+self.rect.h)//2
        self.player_damage = self.attack_data["damage"]
        self.cramming_rect = self.rect.inflate(-TILE_SIZE//2,-TILE_SIZE//2)
        
    def draw_extra(self, screen, offset):
        if pygame.time.get_ticks() - self.last_damage <= self.hit_cooldown:
            mask = pygame.mask.from_surface(self.image)
            surf = mask.to_surface(setcolor="red")
            surf.set_colorkey("black")
            surf.set_alpha(150)
            offsetted_s = self.rect.copy()
            offsetted_s.center -= offset
            screen.blit(surf,offsetted_s)
            self.debug.blits += 1
        
    def other_collisions(self):
        for enemy in self.other_enemies:
            if self.cramming_rect.colliderect(enemy.cramming_rect):
                direction = enemy.pos-self.pos
                #if direction.magnitude() != 0: direction.normalize_ip()
                #direction *= self.size
                self.pos += -vector(direction.x/20,direction.y/20)
        
    def extra_update(self, dt):
        self.cramming_rect.center = self.rect.center
        self.other_collisions()
        if self.cramming_rect.colliderect(self.player.hitbox):
            self.player.stats.damage(self.player_damage)

class Boss(EnemyAttacker):
    def __init__(self, pos, animations, groups, name, font, room):
        super().__init__(pos,animations,groups,name,font,room,BOSS_VISION_RANGE)
        self.assets = self.room.dungeon.assets
        
    def warn(self): WarningMsg(self.rect.midtop+vector(0,0),self.assets["ui"]["emark"],[self.room.visible_top,self.room.updates],self.room)
        
class OgreBoss(Boss):
    def __init__(self, pos, animations, groups, name, font, room, weapon_surf):
        super().__init__(pos, animations, groups, name, font, room)
        self.weapon_ori_s = pygame.transform.scale_by(weapon_surf,0.75)
        self.weapon_offset_r,self.weapon_offset_l = vector(TILE_SIZE//2.5,TILE_SIZE//1.8),vector(-TILE_SIZE//2.5,TILE_SIZE//1.8)
        self.weapon_offset_ru,self.weapon_offset_lu = self.weapon_offset_r+vector(0,-SCALE_FACTOR),self.weapon_offset_l+vector(0,-SCALE_FACTOR)
        self.weapon_angle_r,self.weapon_angle_l,self.swing_start_angle,self.swing_end_angle_r,self.swing_end_angle_l = -45,45,0,-90,90
        self.swing_start_speed,self.swing_speed,self.swing_dir,self.swing_acceleration,self.next_angle,self.weapon_angle=10,0,1,1,0,0
        self.weapon_surf = self.weapon_ori_s; self.weapon_rect = self.weapon_surf.get_rect()
        
        self.last_attack,self.attack_cooldown = 0,2000
        self.player_damage,self.should_damage,self.wait_cooldown = 2,False,400
        self.attack_hitbox = self.rect.inflate(-TILE_SIZE//2,-TILE_SIZE)
        self.notice_hitbox = self.rect.inflate(TILE_SIZE,-TILE_SIZE*1.5)
        
    def draw_extra(self, screen, offset):
        if pygame.time.get_ticks() - self.last_damage <= self.hit_cooldown:
            mask = pygame.mask.from_surface(self.image)
            surf = mask.to_surface(setcolor="red")
            surf.set_colorkey("black"); surf.set_alpha(150)
            offsetted_s = self.rect.copy(); offsetted_s.center -= offset
            screen.blit(surf,offsetted_s); self.debug.blits += 1
        offsetted = self.weapon_rect.copy(); offsetted.center -= offset
        screen.blit(self.weapon_surf,offsetted)
        
    def die(self):
        super().die()
        FxEffect(self.rect.center,self.assets["fx"]["MagicBarrier"],[self.room.visible_top,self.room.updates],self.room,1,1)
    
    def start_attack(self):
        self.can_chase,self.should_damage = False,True
        self.last_attack = pygame.time.get_ticks()
        self.weapon_angle,self.swing_speed = self.swing_start_angle,self.swing_start_speed
        self.next_angle = self.swing_end_angle_r if self.orientation == "right" else self.swing_end_angle_l
        self.swing_dir = 1 if self.orientation == "left" else -1
        self.warn()
        
    def attack(self):
        if self.attack_hitbox.colliderect(self.player.rect): self.player.stats.damage(self.player_damage)
        self.should_damage = False
    
    def extra_update(self, dt):
        # weapon
        self.weapon_surf = pygame.transform.rotate(self.weapon_ori_s,self.weapon_angle)
        is_u = int(self.frame_index)%2 == 0
        offset = (self.weapon_offset_ru if is_u else self.weapon_offset_r) if self.orientation == "right" else (self.weapon_offset_lu if is_u else self.weapon_offset_l)
        pos = self.rect.center + offset
        if self.orientation == "right": self.weapon_rect = self.weapon_surf.get_rect(bottomleft=pos)
        else: self.weapon_rect = self.weapon_surf.get_rect(bottomright=pos)
        
        # movement, attack
        self.notice_hitbox.center = self.rect.center
        if self.orientation == "right": self.attack_hitbox.midleft = self.rect.center
        else: self.attack_hitbox.midright = self.rect.center
        if self.notice_hitbox.colliderect(self.player.rect) and self.can_chase: self.start_attack()
        if not self.can_chase:
            if pygame.time.get_ticks() - self.last_attack >= self.attack_cooldown: self.can_chase = True
            else:
                self.swing_speed += self.swing_acceleration
                self.weapon_angle += self.swing_speed*self.swing_dir*dt
                if self.swing_dir == 1:
                    if self.weapon_angle > self.swing_end_angle_l: self.weapon_angle = self.swing_end_angle_l
                else:
                    if self.weapon_angle < self.swing_end_angle_r: self.weapon_angle = self.swing_end_angle_r
            if self.should_damage:
                if pygame.time.get_ticks()-self.last_attack >= self.wait_cooldown: self.attack()
        else: self.weapon_angle = self.weapon_angle_r if self.orientation == "right" else self.weapon_angle_l

class HellblazeBoss(Boss):
    def __init__(self, pos, animations, groups, name, font, room):
        super().__init__(pos,animations,groups,name,font,room)
        
        self.mouth_hitbox = self.rect.inflate(-TILE_SIZE//2,-TILE_SIZE//2)
        self.mouth_damage = 1
        self.poison_damage = 4
        self.damage_dealt = 0
        self.max_mouth_damage = 2
        
        self.change_mode_time = 0
        self.poison_wait_cooldown = 500
        self.poison_spawn_time = 0
        self.poison_effect = None
        self.last_fireball = 0
        self.fireball_count = 0
        self.fireball_cooldown = 500
        self.small_fireball_count = 8
        self.health/=4
        
    def standard_attack(self):
        before = self.player.stats.health
        self.player.stats.damage(self.mouth_damage)
        if self.player.stats.health != before: self.damage_dealt += self.mouth_damage
        
    def poison_attack(self):
        self.poison_effect = FxEffect(self.rect.center,self.assets["fx"]["PoisonClaw"],[self.room.visible_objects,self.room.updates],self.room,1,1.2)
        self.poison_spawn_time = pygame.time.get_ticks()
        
    def start_fireball_attack(self):
        self.last_fireball = pygame.time.get_ticks()
        self.fireball_count = 0
        
    def change_from_standard(self):
        self.damage_dealt,self.can_chase,self.change_mode_time,self.attack_mode = 0,False,pygame.time.get_ticks(),choice([1,2])
        if self.attack_mode == 1: self.warn()
        if self.attack_mode == 2: self.warn(); self.start_fireball_attack()
        
    def spawn_fireball(self, size):
        sprites = choice([self.assets["fx"]["FireBall"],self.assets["fx"]["FireBall_3"]]) if size == "small" else self.assets["fx"]["FireBall_2"]
        damage,speed_mul = (2,1) if size == "small" else (5,1.5)
        dir = self.player.pos-self.pos
        if dir.magnitude() != 0: dir.normalize_ip()
        Fireball(self.rect.center,sprites,
                 [self.room.visible_objects,self.room.updates,self.room.fireballs],self.room,
                 dir,damage,speed_mul)
        self.fireball_count += 1
        self.last_fireball = pygame.time.get_ticks()
        
    def die(self):
        super().die()
        FxEffect(self.rect.center,self.assets["fx"]["FireCast"],[self.room.visible_top,self.room.updates],self.room,1,1.5)
        FxEffect(self.rect.center,self.assets["fx"]["FireBurst"],[self.room.visible_top,self.room.updates],self.room,1,1.5)
        
    def extra_update(self, dt):
        self.mouth_hitbox.center = self.rect.center
        if self.mouth_hitbox.colliderect(self.player.hitbox): self.standard_attack()
        if self.attack_mode == 0:
            self.can_chase = True
            if self.damage_dealt >= self.max_mouth_damage: self.change_from_standard()
        if not self.can_chase:
            diff = self.player.pos.x-self.pos.x
            if diff >= 0: self.orientation = "right"
            else: self.orientation = "left"
        if self.attack_mode == 1:
            if pygame.time.get_ticks()-self.change_mode_time >= self.poison_wait_cooldown and self.poison_spawn_time == 0: self.poison_attack()
            if self.poison_effect and not self.poison_effect.finished:
                if self.poison_effect.rect.colliderect(self.player.hitbox): self.player.stats.damage(self.poison_damage)
            else:
                if self.poison_spawn_time != 0: self.poison_spawn_time, self.attack_mode,self.poison_effect = 0,0,None
        elif self.attack_mode == 2:
            if pygame.time.get_ticks()-self.last_fireball >= self.fireball_cooldown:
                if self.fireball_count < self.small_fireball_count-1:
                    self.spawn_fireball("small")
                else:
                    self.spawn_fireball("big")
                    self.attack_mode = 0
                
    def draw_extra(self, screen, offset):
        if pygame.time.get_ticks() - self.last_damage <= self.hit_cooldown:
            mask = pygame.mask.from_surface(self.image)
            surf = mask.to_surface(setcolor="red")
            surf.set_colorkey("black")
            surf.set_alpha(150)
            offsetted_s = self.rect.copy()
            offsetted_s.center -= offset
            screen.blit(surf,offsetted_s)
            self.debug.blits += 1
