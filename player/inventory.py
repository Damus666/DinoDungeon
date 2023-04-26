import pygame
from settings import *
import support

@singleton
class Inventory:
    i = None
    def __init__(self, assets):
        Inventory.i = self
        self.display_surface = pygame.display.get_surface()
        self.assets = support.parse_sprites_ratio(assets["items"])
        
        self.slots:list[Slot] = []
        for _ in range(5): self.slots.append(Slot())
            
        self.coins = 0
        self.ui_changed = False
        
        self.weapon = None
        self.effects = {}
        
    def consume_item(self, item):
        self.remove_item(item.name)
        if item.name in POTIONS: self.add_effect(item.name)
            
    def add_effect(self,name): self.effects[name] = {"start":pygame.time.get_ticks(),"duration":POTION_DATA[name]["duration"]}
    def effect_active(self, name): return name in self.effects.keys()
        
    def get_item_surf(self, name): return self.assets[name]
    def get_item_surf_only(self, name): return self.assets[name][0]
        
    def add_coins(self,amount, starting=False):
        self.coins += amount
        self.ui_changed = True
        for i in range(amount):
            if not starting: self.add_floating_coin()
        
    def can_buy(self, price=1): return self.coins >= price
    def can_remove(self, name): return self.has_item(name)
    
    def buy(self, price):
        if self.can_buy(price):
            self.coins -= price; self.ui_changed = True
        
    def empty(self):
        for slot in self.slots: slot.empty()
            
    def has_item(self,name):
        for slot in self.slots:
            if slot.compare(name) and not slot.is_empty(): return True
        return False
    
    def count_item(self, name):
        amount = 0
        for slot in self.slots:
            if slot.compare(name): amount += slot.amount
        return amount
    
    def can_add(self,name):
        for slot in self.slots:
            if slot.is_empty(): return not self.has_item(name)
            if slot.compare(name) and name in STACKABLE: return slot.amount < ITEM_STACKS[name]
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
                    slot.set(item,1)
                    if not starting: self.add_floating_item(item.name)
                    return
                elif slot.compare(item.name) and item.name in STACKABLE:
                    if slot.amount < ITEM_STACKS[item.name]:
                        slot.amount += 1
                        if not starting: self.add_floating_item(item.name)
    
    def remove_item(self, name):
        if self.can_remove(name):
            for slot in self.slots:
                if slot.compare(name):
                    if slot.amount > 1: slot.amount -= 1
                    else: slot.empty()
                    self.shift()
    
    @internal
    def shift(self):
        items = {}
        for slot in self.slots:
            if not slot.is_empty(): items[slot.item] = slot.amount
            slot.empty()
        for i, (item, amount) in enumerate(items.items()): self.slots[i].set(item,amount)
    
@singleton   
class Stats:
    def __init__(self):
        self.max_health = 14
        self.health = self.max_health
        
        self.max_energy = 100
        self.energy = self.max_energy
        
        self.alive = True
        self.last_damage = pygame.time.get_ticks()-INVULNERABILITY_COOLDOWN
        self.last_heal = pygame.time.get_ticks()-HEAL_COOLDOWN
        
    def consume_item(self, item):
        if item.name == "Healing Potion":
            if self.health < self.max_health: self.health = self.max_health
            else: return False, "No need to heal"
            return True,None
        elif item.name in POTIONS: return True,None
        return False, "[ERR] Could not consume item"
    
    # energy
    def consume_energy(self, amount):
        self.energy -= amount
        if self.energy <= 0: self.energy = 0
        
    @property
    def can_damage(self): return pygame.time.get_ticks() -self.last_damage >= INVULNERABILITY_COOLDOWN
    
    # health
    def damage(self,amount):
        if pygame.time.get_ticks() - self.last_damage >= INVULNERABILITY_COOLDOWN:
            self.health -= int(amount)
            if self.health <= 0: self.health = 0; self.alive = False
            self.last_damage = pygame.time.get_ticks()
            
    def heal(self, amount):
        self.health += int(amount); self.last_heal = pygame.time.get_ticks()
        if self.health > self.max_health: self.health = self.max_health
        

class Slot:
    def __init__(self):
        self.item = None
        self.amount = 0
    
    def compare(self, name):
        if not self.is_empty(): return self.item.name == name
        return False
    
    def empty(self): self.item = None; self.amount = 0
    def is_empty(self): return self.item == None or self.amount == 0
    def set(self, item, amount): self.item = item; self.amount = amount
        
class Item:
    def __init__(self,data):
        for key, value in data.items(): setattr(self,key,value)
    