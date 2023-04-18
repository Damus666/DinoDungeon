import pygame
from settings import *
from .static import *
from .animated import *

class Door(Generic):
    def __init__(self, pos, door_assets, groups, orientation, room_connected,teleport_loc, room, transition_dir,dungeon,shift_up=False, shift_left=False, key=None,font=None):
        pos = (pos[0],pos[1]-3*SCALE_FACTOR)
        self.close_image = door_assets["doors_all"] if orientation == "v" else door_assets["doors_all_v"]
        self.open_image = door_assets["doors_all_open"] if orientation == "v" else door_assets["doors_all_v_open"]
        if orientation == "v":
            if shift_up:
                pos = (pos[0],pos[1]-TILE_SIZE*2)
                teleport_loc = (teleport_loc[0],teleport_loc[1]-TILE_SIZE-TILE_SIZE//2)
            pos = (pos[0]-TILE_SIZE,pos[1])
            teleport_loc = (teleport_loc[0]+TILE_SIZE,teleport_loc[1])
        if orientation == "h":
            teleport_loc = (teleport_loc[0],teleport_loc[1]+TILE_SIZE*1.5)
            if shift_left:
                pos = (pos[0],pos[1])
                teleport_loc = (teleport_loc[0]-TILE_SIZE+TILE_SIZE//2, teleport_loc[1])
            else:
                pos = (pos[0]-TILE_SIZE-(self.close_image.get_width()-(32*SCALE_FACTOR)),pos[1])
                teleport_loc = (teleport_loc[0]+TILE_SIZE+TILE_SIZE//2,teleport_loc[1])
            
        super().__init__(pos,self.close_image,groups,room,False,False)
        self.dungeon = dungeon
        self.room_connected = room_connected
        self.door_connected = None
        self.status = "close"
        self.key = key if key != "none" else None
        if orientation == "v":
            self.hitbox.inflate_ip(-TILE_SIZE*2,0)
            Collider((self.hitbox.left-TILE_SIZE,self.hitbox.top+TILE_SIZE-1),(TILE_SIZE,TILE_SIZE),[self.room.collidable],room)
            Collider((self.hitbox.right,self.hitbox.top+TILE_SIZE-1),(TILE_SIZE,TILE_SIZE),[self.room.collidable],room)
        self.interaction_rect = self.hitbox.inflate(TILE_SIZE,TILE_SIZE*2)
        self.teleport_location = teleport_loc
        self.center = vector(self.rect.center)
        self.orientation = orientation
        self.transition_dir = transition_dir
        self.font = font
        self.name_surf = self.font.render(self.room_connected.name,False,"white")
        self.name_rect = self.name_surf.get_rect(center = self.rect.midtop)
        self.name_rect_infalted = self.name_rect.inflate(10,-5)
        self.original_center = self.name_rect.center
        self.force_locked = False
        
    def lock(self): self.force_locked = True; self.change_status("close")
    def unlock(self): self.force_locked = False; self.change_status("open")
        
    def draw_name(self,screen,offset):
        self.name_rect.center = self.original_center-offset
        self.name_rect_infalted.center = self.original_center-offset
        pygame.draw.rect(screen,BG_DARK_COL,self.name_rect_infalted,0,4)
        screen.blit(self.name_surf,self.name_rect)
        self.debug.blits += 2
        
    def can_interact(self, inventory):
        self.debug.updates += 1
        return (self.key == None or inventory.has_item(self.key)) and not self.force_locked
    
    def interact(self):
        self.dungeon.change_room(self.room_connected,self.orientation,self.transition_dir,self.teleport_location)
        for door in self.room.doors: door.change_status("close")
        self.door_connected.change_status("open")
            
    def change_status(self,status):
        self.status = status
        if self.status == "close": self.image = self.close_image
        else: self.image = self.open_image
        
class Crate(Generic):
    def __init__(self, pos, surf, crate_data, groups, smoke_assets, smoke_groups, coin_data, drop_groups,room):
        super().__init__(pos, surf, groups, room,False)
        self.rect.y -= TILE_SIZE//2
        self.hitbox.y -= TILE_SIZE//2
        self.crate_data = crate_data
        self.interaction_rect = self.rect.inflate(TILE_SIZE*2,TILE_SIZE*2)
        self.smoke_assets = smoke_assets
        self.smoke_groups = smoke_groups
        self.coin_data = coin_data
        self.drop_groups = drop_groups
        self.coin_amount = randint(5,20)
        self.items = []
        if "items" in self.crate_data:
            self.items = parse_items_string(self.crate_data)
        
    @external
    def interact(self):
        smoke = FxEffect((self.rect.centerx-TILE_SIZE,self.rect.centery),self.smoke_assets,self.smoke_groups,self.room,1,2)
        if "coins" in self.crate_data:
            for i in range(self.coin_amount):
                vel = vector(randint(-80,80),randint(50,80))
                coin = Coin(self.rect.center,vel,self.coin_data[0],self.coin_data[1],self.coin_data[2],self.coin_data[3],self.room)
        elif "items" in self.crate_data:
            for item in self.items:
                vel = vector(randint(-80,80),randint(50,80))
                drop = Drop(self.rect.center,vel,Inventory.i.get_item_surf_only(item),item,self.drop_groups,self.coin_data[1],self.coin_data[3],self.room)
            
        self.kill()

class Character(AnimatedStatus):
    def __init__(self, pos, animations, groups, room):
        super().__init__(pos, animations, "idle", groups,room, True,False)
        self.pos = vector(self.rect.center)
        self.player = self.room.dungeon.player
        
class Hero(Character):
    def __init__(self, pos, animations, groups, data, font, room):
        super().__init__(pos, animations, groups, room)
        self.data = data
        self.name = "Hero"
        self.id = -1
        if self.data:
            self.asset_name,self.id,self.name = self.data.split(",")
            self.id = int(self.id)
        self.interaction_rect = self.rect.inflate(TILE_SIZE,TILE_SIZE)
        self.interaction_data = None
        if self.id != -1: self.interaction_data = self.room.dungeon.map_script.INTERACTION_DATA[self.id]
        self.font = font
        self.name_surf = self.font.render(self.name,False,"white")
        self.name_rect = self.name_surf.get_rect()
    
    @runtime
    def draw_name(self,screen,offset):
        self.name_rect.midtop = self.rect.midbottom-offset
        self.name_rect.y+=2
        pygame.draw.rect(screen,BG_DARK_COL,self.name_rect.inflate(10,-5),0,4)
        screen.blit(self.name_surf,self.name_rect)
        self.debug.blits += 2
        
