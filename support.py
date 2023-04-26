import pygame, time, math
from settings import *
from os import walk
from os.path import join
from random import randint, choice
from player.inventory import Item
from graphics.spritesheet import *

@helper

# classes
class HealthBar:
    def __init__(self, rect, fill_color, corner_w, has_outline=False, outline_col=None):
        if not has_outline:
            self.bg_rect = CornerRect(rect.inflate(4,4),corner_w,UI_BG_COL)
            self.fill_rect = CornerRect(rect.copy(),corner_w,fill_color)
            self.original = rect
        else:
            self.bg_rect = CornerRect(rect.copy(),corner_w,UI_BG_COL)
            self.fill_rect = CornerRect(rect.copy(),corner_w,fill_color)
            self.original = rect
            self.outline_rect = CornerRect(rect.inflate(4,4),corner_w,outline_col)
        self.has_outline = has_outline
        self.corner_w = corner_w
        
    def draw(self, current_health, max_health):
        if self.has_outline: self.outline_rect.draw()
        self.bg_rect.draw()
        ratio = current_health/max_health
        w = int(self.original.w * ratio)
        if self.fill_rect.original.w != w:
            self.fill_rect.original.w = w
            self.fill_rect.refresh()
        if w >= self.corner_w:
            self.fill_rect.draw()

class CornerRect:
    def __init__(self, rect:pygame.Rect, border_size, color):
        # params
        self.display_surface = pygame.display.get_surface()
        self.original = rect
        self.size = border_size
        self.color = color
        self.refresh()
        
    def set_rect(self, rect):
        self.original = rect
        self.refresh()
        
    def set_topleft(self, pos):
        self.original.topleft = pos
        self.refresh()
        
    def set_center(self, pos):
        self.original.center = pos
        self.refresh()
        
    def refresh(self):
        
        # rect, corners
        self.v_rect = self.original.inflate(-self.size*2,0)
        self.h_rect = self.original.inflate(0,-self.size*2)
        self.corners = [
            (self.h_rect.topleft,self.v_rect.topleft,(self.v_rect.left,self.h_rect.top)),
            (self.h_rect.topright,self.v_rect.topright,(self.v_rect.right,self.h_rect.top)),
            (self.h_rect.bottomleft,self.v_rect.bottomleft,(self.v_rect.left,self.h_rect.bottom)),
            (self.h_rect.bottomright,self.v_rect.bottomright,(self.v_rect.right,self.h_rect.bottom))
        ]
        
        # correct
        self.v_rect.h += 1
        self.h_rect.w += 1
        self.center = self.v_rect.center
        
    def draw(self, debug=None):
        pygame.draw.rect(self.display_surface,self.color,self.h_rect)
        pygame.draw.rect(self.display_surface,self.color,self.v_rect)
        for corner in self.corners: pygame.draw.polygon(self.display_surface,self.color,corner)
        if debug: debug.blits += 7
            
class Timeit:
    def __init__(self):
        self.start_time = 0
        self.end_time = 0
        self.name = "Generic Timeit"
            
    def start(self,name):
        self.name = name
        self.start_time = time.perf_counter()
        return self
        
    def end(self):
        self.end_time = time.perf_counter()
        print(f"{self.name} elapsed: {self.end_time-self.start_time}")
        return self

# math
def angle_to_vec(angle):
    return vector(math.cos(math.radians(angle)),-math.sin(math.radians(angle)))

def weighted_choice(sequence,weights):
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def weighted_choice_combined(sequence_and_weights):
    sequence = [s_a_w[0] for s_a_w in sequence_and_weights]
    weights = [saw[1] for saw in sequence_and_weights]
    weightssum = sum(weights)
    chosen = randint(0,weightssum)
    cweight = 0; i = 0
    for w in weights:
        if inside_range(chosen,cweight,cweight+w): return sequence[i]
        cweight += w; i += 1
        
def lerp(start, end, t): return start * (1 - t) + end * t
            
def inside_range(number:float|int,rangeStart:float|int,rangeEnd:float|int)->bool:
    return number >= min(rangeStart,rangeEnd) and number <= max(rangeStart,rangeEnd)

# generic 
def count_pngs(path):
    count = 0
    for f_name, sub_f, files in walk(path):
        for sub_n in sub_f:
            count += count_pngs(path+"/"+sub_n)
        for f in files:
            if f.endswith("png"):
                count += 1
    return count            

def list_remove_cond(iterable, condition):
    toremove = [el for el in iterable if condition(el)]
    for e in toremove: iterable.remove(e)

# str
def item_from_name(name): return Item({"name":name})
def parse_items_string(string:str): return string.replace("items:","").split(",")

# images
def import_folder(path,convert_alpha = True, scale_factor=True):
    images = []
    for _, _, image_names in walk("assets/graphics/"+path):
        for image_name in image_names:
            full_path = "assets/graphics/"+join(path,image_name)
            image = pygame.image.load(full_path).convert_alpha() if convert_alpha else pygame.image.load(full_path).convert()
            if scale_factor: image = pygame.transform.scale_by(image,SCALE_FACTOR)
            images.append(image)
        break
    return images

def import_folder_dict(path,convert_alpha = True, scale_factor=True):
    images = {}
    for _, sub_f, image_names in walk("assets/graphics/"+path):
        for image_name in image_names:
            full_path = "assets/graphics/"+join(path,image_name)
            image = pygame.image.load(full_path).convert_alpha() if convert_alpha else pygame.image.load(full_path).convert()
            if scale_factor: image = pygame.transform.scale_by(image,SCALE_FACTOR)
            images[image_name.split(".")[0]] = image
        break
    return images

def import_dict_fx(path, scale=2):
    return {"_".join(name.split("_")[0:-1]):pygame.transform.scale_by(image, scale) for name, image in import_folder_dict(path,True,False).items()}

def load(path,convert_alpha = True,scale_factor=True):
    image = pygame.image.load("assets/graphics/"+path+".png").convert_alpha() if convert_alpha else pygame.image.load("assets/graphics/"+path+".png").convert()
    if scale_factor: return pygame.transform.scale_by(image,SCALE_FACTOR)
    return image

def load_scale(path,scale_factor,convert_alpha = True):
    return pygame.transform.scale_by(pygame.image.load("assets/graphics/"+path+".png").convert_alpha() if convert_alpha \
        else pygame.image.load("assets/graphics/"+path+".png").convert() ,scale_factor)
    
def parse_sprites_ratio(assets, size=UI_INNER_SLOT_SIZE):
    sprites = {}
    for name, img in assets.items():
        w,h = img.get_size()
        if w > h:
            ratio = w/size
            image = pygame.transform.scale(img,(int(size),int(h/ratio)))
            sprites[name] = (image,image.get_rect())
        else:
            ratio = h/size
            image = pygame.transform.scale(img,(int(w/ratio),int(size)))
            sprites[name] = (image,image.get_rect())
    return sprites

def only_sprites_from_tuple(sprites): return {name:sprite for name, (sprite,_) in sprites.items()}

# sheets
def load_sheet(path, size, convert_alpha=False,scale=1): return Spritesheet(load(path,convert_alpha,False),size).frames(scale)
def parse_sheets(sheet_dict): return {name:SingleSpritesheet(sheet).frames() for name, sheet in sheet_dict.items()}
        