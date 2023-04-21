import pygame, math
from settings import *
from pygame.sprite import Group
from sprites.sprites import *
from sprites.super import Door
from support import *
from .generator import RoomGenerator

class Room:
    def __init__(self,dungeon,positions,data):
        self.display_surface = pygame.display.get_surface()
        self.dungeon = dungeon
        self.debug = self.dungeon.debug
        self.positions = positions
        self.data = data
        self.player = self.dungeon.player
        self.offset = pygame.Vector2(0,0)
        self.name = self.data["name"]
        self.boss_ui = self.dungeon.ui.states["boss"]
        
        self.visible_bg = CameraGroup(self.player)
        self.visible_floor = CameraGroup(self.player)
        self.visible_walls = CameraGroup(self.player)
        self.visible_objects = CameraGroup(self.player)
        self.visible_top = CameraGroup(self.player)
        
        self.updates = Group()
        self.coins = Group()
        self.doors = Group()
        self.crates = Group()
        self.collidable = Group()
        self.spikes = Group()
        self.drops = Group()
        self.inv_msgs = Group()
        self.enemies = Group()
        self.heros = Group()
        self.fireballs = Group()
        self.end_portal = None
        self.next_rooms:list[Room] = []
        
        self.name_font = pygame.font.Font("assets/fonts/main.ttf",25)
        self.build()
    
    @extend(__init__)
    def build(self):
        assets = self.dungeon.assets
        self.outline_positions = RoomGenerator.get_outline_positions(self.positions)
        for pos in self.positions:
            scaled = RoomGenerator.scale_pos(pos)
            Generic(scaled,RoomGenerator.get_floor_sprite(assets["floor"]),[self.visible_floor],self)
        for spike_pos in self.data["spikes"]:
            scaled = RoomGenerator.scale_pos(spike_pos)
            Spike(scaled,assets["spikes"],[self.visible_walls,self.updates,self.spikes],self)
        for pos in self.outline_positions:
            scaled = RoomGenerator.scale_pos(pos)
            sprites, names = RoomGenerator.get_wall_sprite(self.positions,self.outline_positions,assets["wall"],pos)
            Wall(scaled,sprites[0],[self.visible_walls,self.collidable],self,names[0])
            if names[-1] == "none":
                if sprites[1]: Wall((scaled[0],scaled[1]-TILE_SIZE),sprites[1],[self.visible_walls,self.collidable],self,names[1])
                if sprites[2]: Wall((scaled[0],scaled[1]+TILE_SIZE),sprites[2],[self.visible_floor,self.collidable],self,names[2])
            else:
                Wall((scaled[0],scaled[1]-TILE_SIZE),sprites[1],[self.collidable,self.visible_walls],self,names[1])
                Fountain(scaled,assets["wall"],[self.visible_walls,self.collidable,self.updates],names[0],names[-1],self)
                Fountain((scaled[0],scaled[1]+TILE_SIZE),assets["wall"],[self.visible_walls,self.collidable,self.updates],names[2],names[-1],self)
        for crate_pos,crate_data in self.data["crates"]:
            scaled = RoomGenerator.scale_pos(crate_pos)
            Crate(scaled, assets["crate"],crate_data,[self.visible_objects,self.collidable,self.crates],assets["smoke"]["particles"],[self.visible_walls,self.updates],
                          [assets["coin"]["anim"],assets["coin"]["particle"],[self.visible_objects,self.coins,self.updates],[self.visible_walls,self.updates]],
                          [self.visible_objects,self.drops,self.updates],self)
        for hero_pos,hero_data in self.data["heros"]:
            if not hero_data: hero_data = "lizard_f,0,Hero"
            scaled = RoomGenerator.scale_pos(hero_pos)
            Hero((scaled[0],scaled[1]-TILE_SIZE),assets[hero_data.split(",")[0]],[self.visible_objects,self.updates,self.heros],hero_data,self.name_font,self)
        for enemy_pos, enemy_data in self.data["enemies"]:
            is_boss = "BOSS" in enemy_data
            if is_boss: enemy_data = enemy_data.replace("BOSS","")
            asset_name, real_name = enemy_data.split(",")
            if not real_name.strip(): real_name = asset_name
            scaled = RoomGenerator.scale_pos(enemy_pos)
            if is_boss:
                if "ogre" in asset_name:
                    OgreBoss(scaled,assets[asset_name],[self.visible_objects,self.updates,self.enemies],real_name,self.name_font,self,assets["weapons"]["weapon_mace"])
                if "big_demon" in asset_name:
                    HellblazeBoss(scaled,assets[asset_name],[self.visible_objects,self.updates,self.enemies],real_name,self.name_font,self)
            else:
                SmallEnemy(scaled, assets[asset_name],[self.visible_objects,self.updates,self.enemies],real_name,self.name_font,self)
        if self.data["portal"]:
            scaled = scaled = RoomGenerator.scale_pos(self.data["portal"])
            self.end_portal = StaticFxEffect(scaled,assets["fx"]["MediumStar"],[self.visible_top,self.updates],self,1.5)
        
        self.build_bg()
    
    @extend(build)
    def build_bg(self):
        combined_outlines = self.positions.copy(); combined_outlines.extend(self.outline_positions)
        layer1_outlines = RoomGenerator.get_outline_positions(combined_outlines); combined_outlines.extend(layer1_outlines)
        layer2_outlines = RoomGenerator.get_outline_positions(combined_outlines); combined_outlines.extend(layer2_outlines)
        layer3_outlines = RoomGenerator.get_outline_positions(combined_outlines)
        list_remove_cond(layer2_outlines, lambda el: randint(0,100) <= 50)
        list_remove_cond(layer3_outlines, lambda el: randint(0,100) <= 70)
        layers = layer1_outlines.copy(); layers.extend(layer2_outlines); layers.extend(layer3_outlines); layers.extend(self.outline_positions)
        for tile in layers:
            surf = pygame.Surface((TILE_SIZE,TILE_SIZE)); surf.fill(BG_DARK_COL)
            t = Generic(RoomGenerator.scale_pos(tile),surf,[self.visible_bg],self); t.draw_secondary = False
    
    @external
    def add_door(self, door_pos, door_center,door_dir, room_connected, teleport_loc, transition_dir, key):
        shift_up,shift_left = False, False
        if door_dir == "v" and (door_center[0],door_center[1]+1) in self.positions: shift_up = True
        if door_dir == "h" and (door_center[0]+1,door_center[1]) in self.positions: shift_left = True
        door = Door(door_pos,self.dungeon.assets["door"],[self.visible_walls,self.doors,self.collidable],\
            door_dir,room_connected,teleport_loc,self,transition_dir,self.dungeon,shift_up,shift_left,key,self.name_font)
        self.next_rooms.append((room_connected,door))
        if door_dir == "v":
            for floor in self.visible_floor:
                if floor.hitbox.inflate(-TILE_SIZE//2,-TILE_SIZE//2).colliderect(door.hitbox): floor.kill()
            for wall in self.visible_walls:
                if wall.hitbox.colliderect(door.interaction_rect) and wall is not door:
                    wall.kill()
                    if wall.hitbox.colliderect(door.hitbox):
                        \
        floor = Generic(wall.rect.topleft,self.dungeon.assets["floor"][0],[self.visible_floor,self.collidable],self)
        return door
    
    def drop_item(self, item, pos):
        Drop(pos,(0,0),self.player.inventory.get_item_surf_only(item.name),item.name,
             [self.visible_objects,self.updates,self.drops],self.dungeon.assets["coin"]["particle"],[self.visible_walls,self.updates],self)
    
    def defeated(self, enemy):
        if "lock_room" in enemy.special_actions:
            for door in self.doors:
                door.unlock()
        if "boss_ui" in enemy.special_actions:
            self.boss_ui.end()
    
    def enter(self):
        for enemy in self.enemies:
            if "lock_room" in enemy.special_actions:
                for door in self.doors:
                    door.lock()
            if "boss_ui" in enemy.special_actions:
                self.boss_ui.start(enemy)
    
    @runtime
    def update(self, dt):
        self.debug.updates += 1
        self.player.update(dt)
        self.updates.update(dt)
    
    @external
    def secondary_check(self, door):
        return self.player.pos.distance_to(door.center) <= SECONDARY_DOOR_DIST
    
    @runtime
    def draw_bg(self):
        self.offset.x = self.player.rect.centerx - H_WIDTH
        self.offset.y = self.player.rect.centery - H_HEIGHT
        
        self.visible_bg.custom_draw(self.offset,False)
    
    @runtime
    def draw(self, secondary = False):
        if secondary:
            self.offset.x = self.player.rect.centerx - H_WIDTH
            self.offset.y = self.player.rect.centery - H_HEIGHT
        
        self.visible_floor.custom_draw(self.offset,secondary)
        self.visible_walls.custom_draw(self.offset,secondary)
        self.visible_objects.custom_draw(self.offset,secondary)
        
        if not secondary:
            for door in self.doors: door.draw_name(self.display_surface,self.offset)
            for hero in self.heros: hero.draw_name(self.display_surface,self.offset)
            for enemy in self.enemies: enemy.draw_extra(self.display_surface,self.offset)
        
        if not secondary: self.player.draw(self.offset)
        self.visible_top.custom_draw(self.offset,secondary)
        if not secondary: self.player.draw_extra(self.offset)


class CameraGroup(pygame.sprite.Group):
    def __init__(self, player):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.debug = self.player.debug
    
    @runtime
    def custom_draw(self,offset, secondary=False):
        for sprite in self.spritedict:
            if not secondary or (sprite.draw_secondary and (dst:=self.player.pos.distance_to(vector(sprite.rect.center))) < SECONDARY_DIST):
                offset_rect = sprite.rect.copy()
                offset_rect.center -= offset
                if secondary:
                    mul = dst/SECONDARY_DIST
                    sprite.alpha_image.set_alpha(int((SECONDARY_DIST - dst) / SECONDARY_DIST * 255))
                    self.display_surface.blit(sprite.alpha_image,offset_rect)
                else:
                    self.display_surface.blit(sprite.image,offset_rect)
                self.debug.rendering += 1