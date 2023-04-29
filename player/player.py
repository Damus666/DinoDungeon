import pygame, sys
from settings import *
from sprites.sprites import *
from player.inventory import *
from support import *

@singleton
@runtime
class Player(AnimatedStatus):
    def __init__(self, animations, dungeon):
        super().__init__((0,0),animations,"idle",[],None,True)
        # setup
        self.display_surface = pygame.display.get_surface()
        self.dungeon = dungeon
        self.debug = self.dungeon.debug
        # inventory
        self.inventory = Inventory(dungeon.assets)
        self.stats = Stats(self.indicate_damage)
        # room
        self.current_room = None
        self.next_teleport_loc = (0,0)
        self.cell_room = None
        # images
        self.original_animations = self.animations
        self.flipped_animations = {
            key: [pygame.transform.flip(sprite,True,False) for sprite in value]
            for key, value in self.animations.items()
        }
        # hitbox
        self.hitbox = pygame.Rect(0,0,TILE_SIZE,TILE_SIZE).inflate(-20,-40)
        self.damage_hitbox = self.hitbox.inflate(-TILE_SIZE//4,0)
        self.hitbox_offset = 45
        # stats
        self.pos = vector()
        self.direction = vector()
        self.orientation = "right"
        self.speed = P_SPEED
        self.dashing = False
        self.dash_start = 0
        # data
        self.draw_data = {"door":None,"crate":None,"hero":None}
        self.font1 = pygame.font.Font("assets/fonts/main.ttf",30)
        self.key_data = {"q":False,"f":False}
        # init
        self.give_starter_items("Sword","Fire Resistance","Emerald Staff","Silver Key","Quartz Key",coins=2000)
        self.dungeon.debug.loaded_entities += 1
        
    def finish(self): self.weapon_ui = self.dungeon.ui.states["weapon"]
    
    @extend(__init__)
    def give_starter_items(self, *items,coins=0):
        for item in items: self.inventory.add_item(item_from_name(item),True)
        self.inventory.add_coins(coins,True)
        self.inventory.collect_souls(2000)
        self.inventory.unlock_power("Light Cast")
        self.inventory.unlock_power("Fireball")
    
    # actions
    @external
    def change_room(self, room): self.current_room = room
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
        if item.name in CAN_EQUIP and not self.weapon_ui.attacking:
            self.inventory.weapon = item.name if self.inventory.weapon != item.name else None
            if self.inventory.weapon:
                self.dungeon.ui.states["weapon"].change_weapon(self.inventory.get_item_surf_only(self.inventory.weapon))
        elif item.name in CAN_CONSUME:
            consumed, error = self.stats.consume_item(item)
            if consumed: self.inventory.consume_item(item)
            else: self.spawn_error_msg(error)
            
    def generic_attack(self):
        if not self.inventory.weapon or self.weapon_ui.attacking or self.dashing: return
        stats = ITEM_STATS[self.inventory.weapon]
        speed,fov = stats["speed"],stats["fov"]
        self.weapon_ui.start_attack(speed,fov)
                    
    def finish_attack(self, rect, offset):
        if self.dashing: return
        if self.inventory.weapon == STAFF_NAME: self.finish_staff()
        else: self.finish_weapon(rect, offset)
                
    def finish_weapon(self, rect, offset):
        stats = ITEM_STATS[self.inventory.weapon]
        damage,area, soul_chance= stats["damage"],stats["area"],stats["soul"]
        rect = rect.copy()
        rect.center = self.pos + offset
        for enemy in self.current_room.enemies:
            if rect.colliderect(enemy.rect):
                enemy.damage(damage)
                if randint(0,100) <= soul_chance: self.inventory.collect_souls(1); self.indicate_soul(enemy.rect.midtop)
                if not area: break
        
    def finish_staff(self):
        if not self.inventory.power and len(self.inventory.powers) > 0: self.inventory.select_power(self.inventory.powers[0])
        data = POWERS_DATA[self.inventory.power]
        if not self.inventory.can_power(data["cost"]): return
        self.inventory.use_power(data["cost"])
        direction = vector(pygame.mouse.get_pos())-vector(H_WIDTH,H_HEIGHT)
        if direction.magnitude() != 0: direction.normalize_ip()
        PowerEffect(self.pos.copy(),self.dungeon.assets["fx"][data["effect"]],[self.current_room.visible_top,self.current_room.updates,self.current_room.effects],
                    self.current_room,direction,data)
    
    def can_damage(self): return not self.dashing 
    def indicate_damage(self, amount): DamageIndicator(self.rect.midtop, amount, [self.current_room.visible_top, self.current_room.updates],self.room,"red",self.font1)
    def indicate_soul(self, pos): SoulMsg(pos,self.dungeon.assets["ui"]["soul"],[self.current_room.visible_top,self.current_room.updates],self.current_room)
    
    def dash_particles(self):
        flip = True if self.orientation == "left" else False
        FlippedFx(self.rect.center,self.dungeon.assets["smoke"]["slide"],[self.current_room.visible_floor,self.current_room.updates],self.current_room,flip)       
    
    def dash(self):
        self.stats.consume_energy(DASH_COST)
        self.dashing,self.dash_start = True, pygame.time.get_ticks()
        self.dash_particles()
    
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
    def input(self, dt):
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
        
        self.speed = P_SPEED if not self.dashing else DASH_SPEED
        if self.dashing and pygame.time.get_ticks()-self.dash_start >= DASH_COOLDOWN: self.dashing = False
        if keys[pygame.K_LSHIFT] and self.stats.energy > 0: self.speed = P_SHIFT_SPEED
    
    def reset_event(self): self.key_data = dict.fromkeys(self.key_data.keys(),False)
            
    def items_shortcuts(self, key):
        keys = pygame.key.get_pressed()
        if key == pygame.K_f: self.inventory.weapon = None
        name= pygame.key.name(key)
        if name.isdecimal():
            name = int(name)
            if not keys[pygame.K_LALT]:
                slot = self.inventory.slots[name-1]
                if not slot.is_empty(): self.item_interact(slot.item)
            else:
                self.inventory.select_power(POWERS[name-1])
    
    def event(self, e):
        if e.type == pygame.KEYDOWN:
            self.items_shortcuts(e.key)
            if e.key == pygame.K_e:
                broken = self.crate_collisions(True)
                if not broken:
                    transitioned = self.door_collisions(True)
                    if not transitioned: self.hero_collisions(True)
                self.debug.updates += 3
                    
            if e.key == pygame.K_q: self.key_data["q"] = True
            if e.key == pygame.K_f: self.key_data["f"] = True
            if e.key == pygame.K_LCTRL and self.stats.energy >= DASH_COST: self.dash()
                
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1: self.generic_attack()
    
    # generic
    def move(self, dt):
        if self.weapon_ui.attacking: return
        if self.speed == P_SHIFT_SPEED and self.direction.magnitude() != 0:
            self.stats.consume_energy(SHIFT_COST*dt)
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
     
    def update_stats(self,dt):
        if self.stats.energy < self.stats.max_energy: self.stats.energy += ENERGY_INCREASE*dt
        if self.inventory.effect_active("Energy Drink"): self.stats.energy = self.stats.max_energy
        if pygame.time.get_ticks()-self.stats.last_heal>= HEAL_COOLDOWN:
            if len(self.current_room.enemies.sprites()) <= 0: self.stats.heal(1)
        for name, value in list(self.inventory.effects.items()):
            if pygame.time.get_ticks()-value["start"] >= value["duration"]: del self.inventory.effects[name]
     
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
        
        if self.current_room.end_portal:
            if self.hitbox.colliderect(self.current_room.end_portal.rect): sys.exit("YOU WON!!!")
        
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
                self.draw_data["crate"] = { "center" : crate.rect.center, }
                return True
            
    def hero_collisions(self, is_event):
        if self.dungeon.transition.active or self.dungeon.dialogue.active: return
        for hero in self.current_room.heros:
            if hero.interaction_rect.colliderect(self.hitbox):
                if is_event: self.dungeon.dialogue.start(hero.interaction_data,hero.name)
                self.draw_data["hero"] = { "center":(hero.rect.centerx,hero.rect.centery+TILE_SIZE*1.7), }
                return True
    
    def object_collisions(self):
        # spike
        for spike in self.current_room.spikes:
            if spike.hitbox.colliderect(self.damage_hitbox) and spike.is_on and self.can_damage():
                self.stats.damage(spike.player_damage)
                spike.damaged(); continue
            if self.pos.distance_to(spike.pos) <= SPIKE_ACTIVATION_DIST: 
                if not spike.is_on: spike.is_close()
            else:
                if spike.is_on: spike.is_far()
        # damage
        for sprite in self.current_room.damages:
            if sprite.name == "lava" and self.inventory.effect_active("Fire Resistance"): continue
            if sprite.hitbox.colliderect(self.hitbox) and self.can_damage(): self.stats.damage(sprite.player_damage)
        # coin      
        for coin in self.current_room.coins:
            if coin.hitbox.colliderect(self.hitbox) and coin.can_collect: self.inventory.add_coins(coin.amount); coin.collect()
        # drop
        for drop in self.current_room.drops:
            if drop.hitbox.colliderect(self.hitbox) and drop.can_collect:
                if self.inventory.can_add(drop.name): self.inventory.add_item(item_from_name(drop.name)); drop.collect()
                else: self.drop_collect_fail(drop)
        # fireball    
        for fireball in self.current_room.fireballs:
            if self.hitbox.colliderect(fireball.hitbox) and self.can_damage():
                self.stats.damage(fireball.player_damage)
                fireball.kill()
                FxEffect(self.rect.center,self.dungeon.assets["fx"]["FireBurst"],[self.current_room.visible_top,self.current_room.updates],self.current_room,1,1.5)
        # power
        for power in self.current_room.effects:
            pierced = 0
            for enemy in self.current_room.enemies:
                power.apply_force(enemy)
                if power.hitbox.colliderect(enemy.rect):
                    damaged= enemy.damage(power.player_damage)
                    if damaged: pierced += 1
                    if (fx:=power.hit_effect) != "none" and damaged:
                        FxEffect(enemy.rect.center,self.dungeon.assets["fx"][fx],[self.current_room.visible_top,self.current_room.updates],self.current_room,1,1.5)
                    if pierced >= power.piercing: break
    
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
            surf = mask.to_surface(setcolor="red"); surf.set_colorkey("black"); surf.set_alpha(150)
            self.display_surface.blit(self.image,offsetted); self.display_surface.blit(surf,offsetted)
            self.debug.blits += 2
                            
    def update(self, dt):
        self.input(dt)
        self.get_status()
        self.animate(dt)
        self.move(dt)
        self.update_stats(dt)
        
        self.door_collisions(False)
        self.crate_collisions(False)
        self.hero_collisions(False)
        self.object_collisions()
        self.debug.updates += 8
