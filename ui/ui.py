import pygame
from settings import *
from .uistate import *

@singleton
class UI:
    def __init__(self, assets, day_night, coin_img, player):
        
        self.states:dict[str,UIState] = {
            #UIOverlay(assets),
            "dnc":UIDNC(assets,day_night,player.debug),
            "health":UIHealth(assets,player.stats,player.debug),
            "coins":UICoins(player.inventory,coin_img,player.debug),
            "inventory":UIInventory(player.inventory,player),
            "boss":UIBoss(player.debug),
            "weapon":UIWeapon(player)
        }
        self.state_values = self.states.values()
        
        self.updates = [state for state in self.state_values if hasattr(state,"update")]
    
    @runtime
    def update(self, dt):
        [state.update(dt) for state in self.updates]
    
    @runtime
    def draw(self):
        [state.draw() for state in self.state_values]
    
