from settings import *
from .uistate import *

@singleton
class UI:
    def __init__(self, assets, coin_img, player):
        
        self.states:dict[str,UIState] = {
            #"overlay":UIOverlay(assets),
            #"dnc":UIDNC(assets,day_night,player.debug),
            "health":UIHealth(assets,player.stats,player.debug),
            "coins":UICoinsSouls(player.inventory,coin_img,player.debug,assets["soul1"]),
            "inventory":UIInventory(player.inventory,player),
            "boss":UIBoss(player.debug),
            "weapon":UIWeapon(player),
            "energy":UIEnergy(player,assets),
            "effects":UIEffects(player,assets["effects"],assets),
            "runes":UIRunes(player, assets),
        }
        self.state_values = self.states.values()
        
        self.updates = [state for state in self.state_values if hasattr(state,"update")]
    
    @runtime
    def update(self, dt):
        [state.update(dt) for state in self.updates]
    
    @runtime
    def draw(self):
        [state.draw() for state in self.state_values]
    
