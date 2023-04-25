import pygame, sys
from settings import *
from ui.ui import UI
from runtime.dnc import DNC
from player.player import Player
from .maploader import MapLoader
from .room import Room, RoomGenerator
from sprites.sprites import *
from support import *
from runtime.transition import Transition
from runtime.dialogue import Dialogue
from runtime.debug import Debug

# maps
import maps.DungeonFeatures

@singleton
class Dungeon:
    def __init__(self, assets, clock, map_loaders, map_name):
        # setup
        self.display_surface = pygame.display.get_surface()
        self.assets = assets
        
        # child
        self.debug = Debug(clock)
        self.player = Player(self.assets["lizard_f"],self)
        self.dnc = DNC(self.debug)
        self.ui = UI(self.assets["ui"],self.dnc,self.assets["coin"]["anim"][0],self.player)
        self.maps:dict[str,MapLoader] = map_loaders
        self.map_loader:MapLoader = map_loaders[map_name]
        self.transition = Transition(self)
        self.dialogue = Dialogue(self)
        
        # init
        self.map_script = maps.DungeonFeatures
        self.debug.loaded_sprites = count_pngs("assets")
        self.player.finish()
        
        # dungeon
        self.reset()
        self.build_map()
    
    @external
    def change_room(self, room, orientation,direction, teleport_location):
        self.next_room = room
        self.transition.start("y" if orientation == "v" else "x",direction, room.name)
        self.player.next_teleport_loc = teleport_location
    
    @external
    def mid_transition(self):
        self.current_room = self.next_room; self.current_room.enter()
        self.player.change_room(self.current_room); self.player.teleport()
    
    def reset(self):
        self.current_room:Room= None; self.next_room: Room = None; self.rooms:list[Room] = []
        self.start()
    
    def build_map(self):
        self.corridor = Room(self, self.map_loader.corridor_pos,self.map_loader.corridor_data)
        for i,r_pos in enumerate(self.map_loader.rooms): room = Room(self,r_pos,self.map_loader.room_data[i]); self.rooms.append(room)
        self.current_room = self.rooms[self.map_loader.player_room_index]
        self.player.change_room(self.current_room); self.player.cell_room = self.current_room
        self.build_connections()
    
    @extend(build_map) 
    def build_connections(self):
        for connection in self.map_loader.connections:
            room1,room2 = self.rooms[connection[0]] if connection[0] != -1 else self.corridor, self.rooms[connection[1]] if connection[1] != -1 else self.corridor
            r_dir,d_center = connection[5],connection[4]
            room1pos = connection[2]; room2pos = connection[3]
            door1 = room1.add_door(RoomGenerator.scale_pos(room1pos),d_center,r_dir,room2,RoomGenerator.scale_pos(room2pos),1,connection[-1])
            door2 = room2.add_door(RoomGenerator.scale_pos(room2pos),d_center,r_dir,room1,RoomGenerator.scale_pos(room1pos),-1,connection[-1])
            door1.door_connected = door2; door2.door_connected = door1
    
    @once
    def start(self): self.player.next_teleport_loc = (0,0); self.player.teleport()
    
    @runtime
    def event_loop(self):
        self.player.reset_event()
        self.debug.updates += 2
        for event in pygame.event.get():
            self.debug.event(event)
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            actioned = self.dialogue.event(event)
            self.debug.updates += 2
            if not actioned: self.player.event(event)
    
    @runtime  
    def run(self, dt):
        # update
        self.event_loop()
        self.debug.update(dt)
        ### self.dnc.update(dt)
        self.current_room.update(dt)
        self.transition.update(dt)
        self.dialogue.update(dt)
        self.ui.update(dt)
        # draw 
        self.display_surface.fill(BG_COL)
        self.current_room.draw_bg()
        for room,door in self.current_room.next_rooms: 
            if room.secondary_check(door): room.draw(True)
        self.current_room.draw()
        self.ui.draw()
        self.dialogue.draw()
        self.transition.draw()
        ### self.dnc.draw()
        self.debug.draw()
