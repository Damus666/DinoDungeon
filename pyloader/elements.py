from .data import ElementData,TileData,ObjectData

class Element:
    """Base class for tiles and objects. Holds the element data, position and layer"""
    def __init__(self,position,data,layer,extra):
        self.extra = extra
        self.data:ElementData = data
        self.position:tuple[int,int] = (position[0],position[1])
        self.layer = layer
        
    def __str__(self):
        return str(self.data.id)
    
    def __repr__(self):
        return str(self.data.id)

class Tile(Element):
    """Holds the element data, position, layer and grid position"""
    def __init__(self, position, data,layer,tile_size,extra):
        super().__init__(position, data,layer,extra)
        self.grid_position = (self.position[0]//tile_size,self.position[1]//tile_size)

class Object(Element):
    """Holds the element data, position and layer"""
    def __init__(self, position, data, layer, tile_size,extra):
        super().__init__(position, data, layer,extra)
        self.grid_position = (self.position[0]//tile_size,self.position[1]//tile_size)