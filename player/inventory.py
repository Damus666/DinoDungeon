import pygame
from settings import *

@singleton
class Inventory:
    i = None
    def __init__(self, assets):
        Inventory.i = self
        self.display_surface = pygame.display.get_surface()
        self.assets = self.parse_item_sprites(assets["items"])
        
        self.slots:list[Slot] = []
        for _ in range(5): self.slots.append(Slot())
            
        self.coins = 0
        self.ui_changed = False 
        
    def parse_item_sprites(self, assets):
        sprites = {}
        for name, img in assets.items():
            w,h = img.get_size()
            if w > h:
                ratio = w/UI_INNER_SLOT_SIZE
                image = pygame.transform.scale(img,(int(UI_INNER_SLOT_SIZE),int(h/ratio)))
                sprites[name] = (image,image.get_rect())
            else:
                ratio = h/UI_INNER_SLOT_SIZE
                image = pygame.transform.scale(img,(int(w/ratio),int(UI_INNER_SLOT_SIZE)))
                sprites[name] = (image,image.get_rect())
        return sprites
        
    def get_item_surf(self, name):
        return self.assets[name]
    
    def get_item_surf_only(self, name):
        return self.assets[name][0]
        
    def add_coins(self,amount, starting=False):
        self.coins += amount
        self.ui_changed = True
        for i in range(amount):
            if not starting: self.add_floating_coin()
        
    def can_buy(self, price=1): return self.coins >= price
    def can_remove(self, name): return self.has_item(name)
    
    def buy(self, price):
        if self.can_buy(price):
            self.coins -= price
            self.ui_changed = True
        
    def empty(self):
        for slot in self.slots: slot.empty()
            
    def has_item(self,name):
        for slot in self.slots:
            if slot.compare(name): return True
        return False
    def count_item(self, name):
        amount = 0
        for slot in self.slots:
            if slot.compare(name): amount += 1
        return amount
    
    def can_add(self,name):
        for slot in self.slots:
            if slot.is_empty(): return not self.has_item(name)
        return False
    
    def add_fail_reason(self, name):
        if self.has_item(name): return "has"
        for slot in self.slots:
            if slot.is_empty(): return "ok"
        return "space"
    
    def add_item(self,item, starting = False):
        if self.can_add(item.name):
            for slot in self.slots:
                if slot.is_empty():
                    slot.set(item)
                    if not starting: self.add_floating_item(item.name)
                    return
    
    def remove_item(self, name):
        if self.can_remove(name):
            for slot in self.slots:
                if slot.compare(name): 
                    slot.empty()
                    self.shift()
    
    @internal
    def shift(self):
        items = []
        for slot in self.slots:
            if not slot.is_empty():
                items.append(slot.item)
            slot.empty()
        for i, item in enumerate(items): self.slots[i].set(item)
    
@singleton   
class Stats:
    def __init__(self):
        self.max_health = 10
        self.health = self.max_health
        
        self.max_actions = 5
        self.actions = self.max_actions
        
        self.alive = True
        self.last_damage = pygame.time.get_ticks()-INVULNERABILITY_COOLDOWN
    
    # action
    def reset_actions(self): self.actions = self.max_actions
    def can_act(self): return self.actions > 0
    
    def give_action(self):
        if self.actions < self.max_actions: self.actions += 1
        
    def consume_action(self):
        if self.actions > 0: self.actions -= 1
        
    @property
    def can_damage(self):
        return pygame.time.get_ticks() -self.last_damage >= INVULNERABILITY_COOLDOWN
    
    # health
    def damage(self,amount):
        if pygame.time.get_ticks() - self.last_damage >= INVULNERABILITY_COOLDOWN:
            self.health -= int(amount)
            if self.health <= 0: self.health = 0; self.alive = False
            self.last_damage = pygame.time.get_ticks()
            
    def heal(self, amount):
        self.health += int(amount)
        if self.health > self.max_health: self.health = self.max_health
        

class Slot:
    def __init__(self):
        self.item = None
    
    def compare(self, name):
        if not self.is_empty(): return self.item.name == name
        return False
    
    def empty(self): self.item = None
    def is_empty(self): return self.item == None
    def set(self, item): self.item = item
        
class Item:
    def __init__(self,data):
        for key, value in data.items(): setattr(self,key,value)
    