from settings import *
from support import *

@static
@helper
class RoomGenerator:
    @staticmethod
    @external
    def get_wall_sprite(positions, outline, assets, pos):
        x,y = pos
        dirs = {
            "left":(x-1,y),
            "right":(x+1,y),
            "top":(x,y-1),
            "bottom":(x,y+1),
        }
        in_pos = dict.fromkeys(dirs.keys(),False)
        in_wall = dict.fromkeys(dirs.keys(),False)
        in_smthing = dict.fromkeys(dirs.keys(),False)
        for name, p in dirs.items():
            if p in positions: in_pos[name] = True
            if p in outline: in_wall[name] = True 
            if p in positions or p in outline: in_smthing[name] = True   
            
        main_name,name_extra,top_name,top_asset,bottom_name,bottom_asset,f_col = "mid","none","none",None,"none",None,"none"
        
        if not in_wall["left"]: 
            main_name = "left"
            if in_pos["left"] and not in_wall["right"]: main_name = "right"
        elif not in_wall["right"]:
            main_name = "right"
            if in_pos["right"] and not in_wall["left"]: main_name = "left"
        if not in_smthing["left"]:
            main_name = "side_left"
            if not in_smthing["bottom"]: main_name = "side_left_mid"
        if not in_smthing["right"]:
            main_name = "side_right"
            if not in_smthing["bottom"]: main_name = "side_right_mid"
        
        if not in_wall["top"] or not in_wall["bottom"]:
            if main_name == "mid": top_name = "top_mid"
            if main_name == "left": top_name = "top_left"
            if main_name == "right": top_name ="top_right"
            if main_name == "side_left": top_name = "top_corner_left"
            if main_name == "side_right": top_name = "top_corner_right"
            
        if main_name == "mid":
            if randint(0,100) < 30:
                alternatives = WALL_MID_ALTERNATIVES_ALL if in_pos["bottom"] else WALL_MID_ALTERNATIVES_T
                main_name = weighted_choice_combined(alternatives)
                if main_name == "fountain":
                    name_extra = choice(FOUNTAIN_COLORS)
                    top_name = "fountain_top"
                    if in_pos["bottom"]: bottom_name = "fountain_bottom"
                    f_col = name_extra
                if main_name == "banner": name_extra = choice(BANNER_COLORS)
                if main_name == "column":
                    top_name = "column_top"
                    if in_pos["bottom"]: bottom_name = "column_bottom"
                if main_name == "goo": bottom_name = "goo_base"
                
        real_name = RoomGenerator.get_real_wall_name(main_name,name_extra)
        real_top = RoomGenerator.get_real_wall_name(top_name,name_extra)
        real_bottom = RoomGenerator.get_real_wall_name(bottom_name,name_extra)
        if real_top != "none": top_asset = assets[real_top]
        if real_bottom != "none": bottom_asset = assets[real_bottom]
        return (assets[real_name], top_asset, bottom_asset),(main_name,top_name,bottom_name,f_col)
    
    @staticmethod
    @external
    def get_floor_sprite(assets): return weighted_choice(assets,FLOOR_WEIGHTS)
            
    @staticmethod
    @internal
    def get_real_wall_name(main_name, name_extra):
        if main_name in WALL_NAMES_LOOKUP: return WALL_NAMES_LOOKUP[main_name]
        else:
            match main_name:
                case "banner": return f"wall_banner_{name_extra}"
                case "fountain": return f"wall_fountain_mid_{name_extra}_anim_f0"
                case "fountain_bottom": return f"wall_fountain_basin_{name_extra}_anim_f0"
    
    @staticmethod
    @external
    def get_outline_positions(positions):
        outline = []
        for pos in positions:
            x,y = pos; dirs = [(x+1,y),(x-1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)]
            for dir in dirs:
                if not dir in positions:
                    if not dir in outline: outline.append(dir) 
        return outline
    
    @staticmethod
    @internal
    def dirs(pos): x,y = pos; return [(x+1,y),(x-1,y),(x,y-1),(x,y+1),(x-1,y-1),(x+1,y+1),(x-1,y+1),(x+1,y-1)]
    @staticmethod
    @external
    def scale_pos(pos): return (pos[0]*TILE_SIZE,pos[1]*TILE_SIZE)
    @staticmethod
    @external
    def add_pos(pos1,pos2): return (pos1[0]+pos2[0],pos1[1]+pos2[1])
        


