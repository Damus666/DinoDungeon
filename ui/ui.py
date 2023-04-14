import pygame
from settings import *
from .uistate import *

@singleton
class UI:
    def __init__(self, assets, day_night, coin_img, player):
        
        self.states:list[UIState] = [
            #UIOverlay(assets),
            UIDNC(assets,day_night),
            UIHealth(assets,player.stats),
            UICoins(player.inventory,coin_img),
            UIInventory(player.inventory,player)
        ]
        
        self.updates = [state for state in self.states if hasattr(state,"update")]
    
    @runtime
    def update(self, dt):
        for state in self.updates: state.update(dt)
    
    @runtime
    def draw(self):
        for state in self.states: state.draw()
    
