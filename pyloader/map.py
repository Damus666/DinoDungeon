from .layer import Layer
from .elements import Tile,Object
from .data import TileData,ObjectData,Data

class MapSettings:
    """Holds the settings of the map such as map size and tile size"""
    def __init__(self,map_size,tile_size):
        self.map_size:tuple[int,int] = (map_size[0],map_size[1])
        self.tile_size:int = tile_size
        
    def __str__(self):
        return f"Map Settings:\n\tTile Size: {self.tile_size}\n\tMap Size: {self.map_size[0]},{self.map_size[1]}"
    
    def __repr__(self):
        lb,rb = "{","}"
        return f"Map Settings = {lb}\n\tTile Size = {self.tile_size},\n\tMap Size = {lb}x = {self.map_size[0]}, y = {self.map_size[1]}{rb}\n{rb}"

class Map:
    """Holds the map information such as settings, layers and data"""
    def __init__(self,data_dict):
        self.settings:MapSettings = MapSettings(data_dict["settings"]["map_size"],data_dict["settings"]["tile_size"])
        self.layers:list[Layer] = list()
        self.data:Data = Data()
        
        for tile in data_dict["tiles"]:
            id,path = tile["id"],tile["path"]
            if tile["type"] == "tile":
                self.data.tiles.append(TileData(id,path))
            elif tile["type"] == "object":
                self.data.objects.append(ObjectData(id,path))
                
        for layer in data_dict["layers"]:
            self.layers.append(Layer(layer["name"],layer["visible"],self.data,self,layer["tiles"]))
            
    def get(self,layer_name):
        """Return the layer with the specified name if any. can also use Map[layer_name]"""
        for l in self.layers:
            if l.name == layer_name:
                return l
            
    def __getitem__(self,index):
        return self.get(index)