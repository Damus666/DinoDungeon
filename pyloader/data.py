class ElementData:
    """Base class for element data. Holds the id and the path file name"""
    type = "none"
    def __init__(self,id,path):
        self.id = id
        self.path = path
        
    def __str__(self):
        return f"({self.id},{self.path})"
    
    def __repr__(self):
        return f"{self.type.title()}(id={self.id},path={self.path})"

class TileData(ElementData):
    """Holds the id and the path file name for a tile"""
    type = "tile"
    def __init__(self, id, path):
        super().__init__(id, path)

class ObjectData(ElementData):
    """Holds the id and the path file name for an object"""
    type = "object"
    def __init__(self, id, path):
        super().__init__(id, path)

class Data:
    """Holds the tiles and objects data as lists"""
    def __init__(self):
        self.tiles:list[TileData] = list()
        self.objects:list[ObjectData] = list()
        
    def get_tile(self,id):
        """Return the tile with an id if any."""
        for tile in self.tiles:
            if tile.id == id:
                return tile
    
    def get_object(self,id):
        """Return the object with an id if any."""
        for obj in self.objects:
            if obj.id == id:
                return obj
            
    def get(self,id):
        """Return the tile or object with an id if any. Can also use Data[id]"""
        for tile in self.tiles:
            if tile.id == id:
                return tile
        for obj in self.objects:
            if obj.id == id:
                return obj
            
    def __getitem__(self,index):
        return self.get(index)
        
    def __str__(self):
        string = "Tiles:\n"
        for t in self.tiles:
            string+= f"\t{t}\n"
        string += "Objects:\n"
        for o in self.objects:
            string += f"\t{o}\n"
        return string
            
    def __repr__(self):
        string = "Data = {\n"
        string += "\tTiles = [\n"
        for t in self.tiles:
            string += f"\t\t{repr(t)}\n"
        string += "\t],\n\tObjects = [\n"
        for o in self.objects:
            string += f"\t\t{repr(o)}\n"
        string += "\t]\n{"
        return string