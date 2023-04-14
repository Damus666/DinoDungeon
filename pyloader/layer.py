from .elements import Tile,Object
from .data import ElementData

class Layer:
    """Holds the information of a layer such as name, visibility, tiles, objects, map and a grid with ids"""
    def __init__(self,name,visible,data,map,tiles_data):
        self.name:str = name
        self.visible:bool = visible
        self.tiles:list[Tile] = list()
        self.objects:list[Object] = list()
        self.grid : list[list[Tile|int]] = list()
        self.map = map
        
        for tile in tiles_data:
            elementdata:ElementData = data.get(tile["id"])
            if elementdata.type == "tile":
                self.tiles.append(Tile(tile["position"],elementdata,self,self.map.settings.tile_size,tile["extra"]))
            elif elementdata.type == "object":
                self.objects.append(Object(tile["position"],elementdata,self,self.map.settings.tile_size,tile["extra"]))
        
        def search(x,y):
            for t in self.tiles:
                if t.grid_position[0] == x and t.grid_position[1] == y:
                    return t.data.id
            return -1
        
        for rowi in range(self.map.settings.map_size[1]):
            row = list()
            for coli in range(self.map.settings.map_size[0]):
                row.append(search(coli,rowi))
            self.grid.append(row)
        
    def grid_repr(self):
        """Return the grid as a string in a human-readable way"""
        def rowstr(obj):
            string = ""
            for el in obj:
                string += str(el) if el != -1 else ""+","
            return string.removesuffix(",")
        string = ""
        for l in self.grid:
            string += rowstr(l)+"\n"
        return string
                
    def __str__(self):
        vstr = "visible" if self.visible else "hidden"
        return f"[{self.name}, {vstr}, grid = ...]"
    
    def __repr__(self):
        return f"Layer(name = {self.name}, visible = {self.visible}, grid = ...)"