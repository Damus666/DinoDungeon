import pygame
from settings import *
import pytilekit
from pyloader.map import Map
from support import *


@singleton
@helper
class MapLoader:
    def __init__(self, name):
        self.room_pos = []
        self.corridor_pos = []
        self.door_pos = []
        self.player_offset = (0, 0)
        self.player_pos = (0, 0)
        self.object_data = []

        self.rooms = []
        self.room_data = []
        self.corridor_data = {"crates": [], "spikes": [
        ], "name": "Corridor", "heros": [], "enemies": [],"portal":False}
        self.connections = []
        self.player_room_index = []
        
        self.load(name)

    def load(self, name):
        with open(f"maps/{name}.json", "r") as file:
            dugneon_map = pytilekit.load(file)
            self.get_positions(dugneon_map)
            self.get_rooms()
            self.get_connections()
            self.get_room_data()
            self.player_room_index = self.get_room_index((0, 0))

    @extend(load)
    def get_room_data(self):
        for room in self.rooms:
            self.room_data.append({"crates": [], "spikes": [], "name": "Generic", "heros": [
            ], "enemies": [], "portal":False})
        for obj_data in self.object_data:
            room_i = self.get_room_index(obj_data[0])
            obj_id = obj_data[1]
            if room_i == -1: room = self.corridor_data
            else: room = self.room_data[room_i]
            match obj_id:
                case "crate": room["crates"].append((obj_data[0], obj_data[2] if obj_data[2] else "coins"))
                case "spike": room["spikes"].append(obj_data[0])
                case "room_name": room["name"] = obj_data[2] if obj_data[2] else "Generic"
                case "hero": room["heros"].append((obj_data[0], obj_data[2] if obj_data[2] else None))
                case "enemy": room["enemies"].append((obj_data[0], obj_data[2] if obj_data[2] else None))
                case "portal": room["portal"] = obj_data[0]

    @extend(load)
    def get_rooms(self):
        room_pos_set = set(self.room_pos)
        room_adj = {}
        for pos in self.room_pos:
            adj_tiles = []
            for x in range(pos[0]-1, pos[0]+2):
                for y in range(pos[1]-1, pos[1]+2):
                    adj_pos = (x, y)
                    if adj_pos in room_pos_set and adj_pos != pos: adj_tiles.append(adj_pos)
            for adj_pos in adj_tiles:
                if adj_pos in room_adj: room_adj[adj_pos].update(adj_tiles)
                else: room_adj[adj_pos] = set(adj_tiles)
            if pos in room_adj: room_adj[pos].update(adj_tiles)
            else: room_adj[pos] = set(adj_tiles)
        self.rooms = []
        visited = set()
        for pos in self.room_pos:
            if pos not in visited:
                room = set([pos])
                stack = [pos]
                while stack:
                    curr_pos = stack.pop()
                    visited.add(curr_pos)
                    if curr_pos in room_adj:
                        room.update(room_adj[curr_pos])
                        for adj_pos in room_adj[curr_pos]:
                            if adj_pos not in visited: stack.append(adj_pos)
                self.rooms.append(list(room))

    @extend(load)
    def get_connections(self):
        for door, door_extra in self.door_pos:
            data = [-2, -2, (0, 0), (0, 0), (0, 0)]
            right, left, bottom, top = ( door[0]+1, door[1]), (door[0]-1, door[1]), (door[0], door[1]+1), (door[0], door[1]-1)
            r_idx, l_idx, b_idx, t_idx = self.get_room_index(right), self.get_room_index(left),\
                                        self.get_room_index(bottom), self.get_room_index(top)
            if r_idx != l_idx: data = [l_idx, r_idx, left, right, door,"h", door_extra if door_extra else None]
            elif t_idx != b_idx: data = [t_idx, b_idx, top, bottom, door, "v", door_extra if door_extra else None]

            self.connections.append(data)

    @internal
    def get_room_index(self, pos):
        if pos in self.corridor_pos: return -1
        for ri, room in enumerate(self.rooms):
            if pos in room: return ri
        return -2

    @internal
    def get_tile_rooms(self, pos):
        dirs = [(pos[0]+1, pos[1]), (pos[0]-1, pos[1]), (pos[0], pos[1]+1), (pos[0], pos[1]-1)]
        for dir in dirs:
            room = self.get_tile_room(dir)
            if room: return room

    @internal
    def get_tile_room(self, pos):
        for room in self.rooms:
            if pos in room: return room
        return None

    @extend(load)
    def get_positions(self, dungeon_map: Map):
        self.player_offset = dungeon_map.get("player").objects[0].grid_position

        for tile in dungeon_map.get("rooms").tiles:
            self.room_pos.append(self.offset(tile.grid_position))

        for tile in dungeon_map.get("corridor").tiles:
            self.corridor_pos.append(self.offset(tile.grid_position))

        for obj in dungeon_map.get("doors").tiles:
            self.door_pos.append((self.offset(obj.grid_position), obj.extra))

        for tile in dungeon_map.get("objects").tiles:
            data = (self.offset(tile.grid_position), OBJECT_ID_LOOKUP[tile.data.id], tile.extra)
            if data not in self.object_data:
                self.object_data.append(data)

    @internal
    def offset(self, pos): return (int(pos[0]-self.player_offset[0]), int(pos[1]-self.player_offset[1]))
