import pygame
from settings import *
from sprites.sprites import *
from player.inventory import *
from support import *

@singleton
@runtime
class Player(AnimatedStatus):
    def __init__(self, animations, dungeon):
        super().__init__((0,0),animations,"idle",[],None,True)
        self.display_surface = pygame.display.get_surface()
        self.dungeon = dungeon
        self.debug = self.dungeon.debug
        self.inventory = Inventory(dungeon.assets)
        self.stats = Stats()
        self.current_room = None
        self.next_teleport_loc = (0,0)
        self.cell_room = None
        
        self.original_animations = self.animations
        self.flipped_animations = {
            key: [pygame.transform.flip(sprite,True,False) for sprite in value]
            for key, value in self.animations.items()
        }
        self.hitbox = pygame.Rect(0,0,TILE_SIZE,TILE_SIZE).inflate(-20,-40)
        self.damage_hitbox = self.hitbox.inflate(-TILE_SIZE//4,0)
        self.hitbox_offset = 45
        self.pos = vector()
        self.direction = vector()
        self.orientation = "right"
        self.speed = P_SPEED
        self.dungeon.debug.loaded_entities += 1
        
        self.draw_data = {"door":None,"crate":None,"hero":None}
        self.font1 = pygame.font.Font("assets/fonts/main.ttf",30)
        self.key_data = {"q":False,"f":False}
        
        self.give_starter_items("Silver Key",coins=30)
    
    @extend(__init__)
    def give_starter_items(self, *items,coins=0):
        for item in items:
            self.inventory.add_item(item_from_name(item),True)
        self.inventory.add_coins(coins,True)
    
    # actions
    @external
    def change_room(self, room):
        self.current_room = room
    @external
    def teleport(self):
        self.direction = vector(); self.rect.center = self.next_teleport_loc
        self.pos.x = self.rect.centerx; self.pos.y = self.rect.centery
        self.hitbox.centerx = self.rect.centerx; self.hitbox.centery = self.rect.centery-self.hitbox_offset
        
    @external
    def shop_action(self,button):
        has_requirements = False
        if button.price_name == "coins": has_requirements = self.inventory.can_buy(button.price_amount)
        else: has_requirements = self.inventory.has_item(button.price_name) and self.inventory.count_item(button.price_name) >= button.price_amount
        if not has_requirements: return
        if button.price_name == "coins": self.inventory.buy(button.price_amount)
        else: self.inventory.remove_item(button.price_name)
        if button.item_name == "coins": self.inventory.add_coins(button.amount)
        else:
            for i in range(button.amount): self.current_room.drop_item(item_from_name(button.item_name),self.hitbox.center)
            
    def drop_item(self, item):
        self.inventory.remove_item(item.name)
        self.current_room.drop_item(item,(self.pos.x,self.pos.y+TILE_SIZE*1.5))
    
    def item_interact(self, item):
        if item.name in CAN_EQUIP:
            self.inventory.weapon = item.name if self.inventory.weapon != item.name else None
            if self.inventory.weapon:
                self.dungeon.ui.states["weapon"].change_weapon(self.inventory.get_item_surf_only(self.inventory.weapon))
        elif item.name in CAN_CONSUME:
            consumed, error = self.stats.consume_item(item)
            if consumed: self.inventory.consume_item(item)
            else: self.spawn_error_msg(error)
            
    def generic_attack(self):
        if self.inventory.weapon:
            stats = ITEM_STATS[self.inventory.weapon]
            damage,area = stats["damage"],stats["area"]
            rect,offset = self.dungeon.ui.states["weapon"].get_data()
            rect = rect.copy()
            rect.center = self.pos + offset
            for enemy in self.current_room.enemies:
                if rect.colliderect(enemy.rect):
                    enemy.damage(damage)
                    if not area: break
            
    
    # messages
    @internal
    def drop_collect_fail(self, drop):
        reason = self.inventory.add_fail_reason(drop.name)
        for inv_msg in self.current_room.inv_msgs:
            if inv_msg.drop == drop: return
        InventoryInfoMsg(drop.rect.center,ADD_FAIL_MESSAGES[reason],self.font1,drop,[self.current_room.visible_top,self.current_room.updates,self.current_room.inv_msgs],self.current_room)
    @internal
    def spawn_error_msg(self, message):
        pos = (self.rect.centerx,self.rect.bottom+TILE_SIZE//2)
        InventoryInfoMsg(pos,message,self.font1,None,[self.current_room.visible_top,self.current_room.updates,self.current_room.inv_msgs],self.current_room)
    
    # RUNTIME
    # event
    def input(self):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_a]: self.direction.x = -1; self.orientation = "left"
        elif keys[pygame.K_d]: self.direction.x = 1; self.orientation = "right"
        else: self.direction.x = 0
        
        if keys[pygame.K_w]: self.direction.y = -1
        elif keys[pygame.K_s]: self.direction.y = 1
        else: self.direction.y = 0
        
        if self.dungeon.transition.active or self.dungeon.dialogue.active:
            self.direction.x,self.direction.y = 0,0
        
        if self.direction.length() != 0: self.direction.normalize_ip()
    
    def reset_event(self):
        self.key_data = dict.fromkeys(self.key_data.keys(),False)
            
    def items_shortcuts(self, key):
        if key == pygame.K_f:
            self.inventory.weapon = None
        name= pygame.key.name(key)
        if name.isdecimal():
            name = int(name)
            slot = self.inventory.slots[name-1]
            if not slot.is_empty():
                self.item_interact(slot.item)
    
    def event(self, e):
        if e.type == pygame.KEYDOWN:
            self.items_shortcuts(e.key)
            if e.key == pygame.K_e:
                broken = self.crate_collisions(True)
                if not broken:
                    transitioned = self.door_collisions(True)
                    if not transitioned: self.hero_collisions(True)
                self.debug.updates += 3
                    
            if e.key == pygame.K_q:
                self.key_data["q"] = True
            if e.key == pygame.K_f:
                self.key_data["f"] = True
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                self.generic_attack()
    
    # generic
    def move(self, dt):
        self.pos.x += self.direction.x*self.speed*dt
        self.rect.centerx = round(self.pos.x)
        self.hitbox.centerx = self.rect.centerx
        self.collisions("horizontal")
        
        self.pos.y += self.direction.y*self.speed*dt
        self.rect.centery= round(self.pos.y)
        self.hitbox.centery = self.rect.centery+self.hitbox_offset
        self.collisions("vertical")
        
        self.damage_hitbox.center = self.hitbox.center
 
    def get_status(self):
        status = "idle"
        if self.direction.x != 0 or self.direction.y != 0: status = "run"
        if self.orientation == "left": self.animations = self.flipped_animations
        else: self.animations = self.original_animations
        self.set_status(status, True)
     
    # collisions   
    def collisions(self, direction):
        for sprite in self.current_room.collidable:
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == "horizontal":
                    self.hitbox.right = sprite.hitbox.left if self.direction.x > 0 else self.hitbox.right
                    self.hitbox.left = sprite.hitbox.right if self.direction.x < 0 else self.hitbox.left
                    self.rect.centerx, self.pos.x = self.hitbox.centerx, self.hitbox.centerx
                    self.direction.x = 0
                else:
                    self.hitbox.top = sprite.hitbox.bottom if self.direction.y < 0 else self.hitbox.top
                    self.hitbox.bottom = sprite.hitbox.top if self.direction.y > 0 else self.hitbox.bottom
                    self.rect.centery, self.pos.y = self.hitbox.centery-self.hitbox_offset, self.hitbox.centery-self.hitbox_offset
                    self.direction.y = 0
        
    def door_collisions(self, is_event):
        if self.dungeon.transition.active or self.dungeon.dialogue.active: return
        for door in self.current_room.doors:
            if door.interaction_rect.colliderect(self.hitbox):
                can = False
                if door.can_interact(self.inventory):
                    if is_event: door.interact()
                    can = True
                self.draw_data["door"] = {
                    "center": door.rect.center,
                    "key":door.key,
                    "can":can,
                    "can_txt": "Enter [E]" if door.status == "close" else "Exit [E]",
                    "locked":door.force_locked
                }
                return True
                
    def crate_collisions(self, is_event):
        if self.dungeon.transition.active or self.dungeon.dialogue.active: return
        for crate in self.current_room.crates:
            if crate.interaction_rect.colliderect(self.hitbox):
                if is_event: crate.interact()
                self.draw_data["crate"] = {
                    "center" : crate.rect.center,
                }
                return True
            
    def hero_collisions(self, is_event):
        if self.dungeon.transition.active or self.dungeon.dialogue.active: return
        for hero in self.current_room.heros:
            if hero.interaction_rect.colliderect(self.hitbox):
                if is_event:
                    self.dungeon.dialogue.start(hero.interaction_data,hero.name)
                self.draw_data["hero"] = {
                    "center":(hero.rect.centerx,hero.rect.centery+TILE_SIZE*1.7),
                }
                return True
            
    def spike_collisions(self):
        for spike in self.current_room.spikes:
            if spike.hitbox.colliderect(self.damage_hitbox) and spike.is_on:
                self.stats.damage(spike.player_damage)
                spike.damaged(); continue
            if self.pos.distance_to(spike.pos) <= SPIKE_ACTIVATION_DIST: 
                if not spike.is_on: spike.is_close()
            else:
                if spike.is_on: spike.is_far()
                    
    def coin_collisions(self):
        for coin in self.current_room.coins:
            if coin.hitbox.colliderect(self.hitbox) and coin.can_collect: self.inventory.add_coins(1); coin.collect()
    
    def drop_collisions(self):
        for drop in self.current_room.drops:
            if drop.hitbox.colliderect(self.hitbox) and drop.can_collect:
                if self.inventory.can_add(drop.name): self.inventory.add_item(item_from_name(drop.name)); drop.collect()
                else: self.drop_collect_fail(drop)
    
    # update
    def draw_extra(self,offset):
        if self.draw_data["door"]:
            requiredkey = self.draw_data["door"]["key"]
            
            txt = self.draw_data["door"]["can_txt"]
            if not self.draw_data["door"]["can"]:
                if not self.draw_data["door"]["locked"]: txt = f"Require: {requiredkey}" 
                else: txt = f"Locked"
            t_surf = self.font1.render(txt,False,"white")
            t_rect = t_surf.get_rect(center=self.draw_data["door"]["center"]-offset)
            
            pygame.draw.rect(self.display_surface,UI_BG_COL,t_rect.inflate(10,0),0,4)
            self.display_surface.blit(t_surf,t_rect)
            
            self.draw_data["door"] = None
            self.debug.blits += 2
            
        if self.draw_data["crate"]:
            t_surf = self.font1.render("Break [E]",False,"white")
            t_rect = t_surf.get_rect(center=self.draw_data["crate"]["center"]-offset)
            
            pygame.draw.rect(self.display_surface,UI_BG_COL,t_rect.inflate(10,0),0,4)
            self.display_surface.blit(t_surf,t_rect)
            
            self.draw_data["crate"] = None
            self.debug.blits += 2
            
        if self.draw_data["hero"]:
            t_surf = self.font1.render("Talk [E]",False,"white")
            t_rect = t_surf.get_rect(center=self.draw_data["hero"]["center"]-offset)
            
            pygame.draw.rect(self.display_surface,UI_BG_COL,t_rect.inflate(10,0),0,4)
            self.display_surface.blit(t_surf,t_rect)
            
            self.draw_data["hero"] = None
            self.debug.blits += 2
            
    def draw(self,offset):
        offsetted = self.rect.copy()
        offsetted.center -= offset
        if self.stats.can_damage:
            self.display_surface.blit(self.image,offsetted)
            self.debug.blits += 1
        else:
            mask = pygame.mask.from_surface(self.image)
            surf = mask.to_surface(setcolor="red")
            surf.set_colorkey("black")
            surf.set_alpha(150)
            self.display_surface.blit(self.image,offsetted)
            self.display_surface.blit(surf,offsetted)
            self.debug.blits += 2
                            
    def update(self, dt):
        self.input()
        self.get_status()
        self.animate(dt)
        self.move(dt)
        
        self.door_collisions(False)
        self.crate_collisions(False)
        self.hero_collisions(False)
        self.coin_collisions()
        self.drop_collisions()
        self.spike_collisions()
        self.debug.updates += 11
