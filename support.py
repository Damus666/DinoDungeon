import pygame, time
from settings import *
from os import walk
from os.path import join
from random import randint, choice
from player.inventory import Item

@helper

class CornerRect:
    def __init__(self, rect:pygame.Rect, border_size, color):
        # params
        self.display_surface = pygame.display.get_surface()
        self.original = rect
        self.size = border_size
        self.color = color
        
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
        
    def draw(self):
        pygame.draw.rect(self.display_surface,self.color,self.h_rect)
        pygame.draw.rect(self.display_surface,self.color,self.v_rect)
        for corner in self.corners: pygame.draw.polygon(self.display_surface,self.color,corner)
            
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
            
def list_remove_cond(iterable, condition):
    toremove = []
    for el in iterable:
        if condition(el): toremove.append(el)
    for e in toremove: iterable.remove(e)

def item_from_name(name): return Item({"name":name})

def import_folder(path,convert_alpha = True, scale_factor=True):
    images = []
    for _, _, image_names in walk("assets/graphics/"+path):
        for image_name in image_names:
            full_path = join(path,image_name)
            full_path = "assets/graphics/"+full_path
            image = pygame.image.load(full_path).convert_alpha() if convert_alpha else pygame.image.load(full_path).convert()
            if scale_factor: image = pygame.transform.scale(image,(int(image.get_width()*SCALE_FACTOR),int(image.get_height()*SCALE_FACTOR)))
            images.append(image)
    return images

def import_folder_dict(path,convert_alpha = True, scale_factor=True):
    images = {}
    for _, _, image_names in walk("assets/graphics/"+path):
        for image_name in image_names:
            full_path = join(path,image_name)
            full_path = "assets/graphics/"+full_path
            image = pygame.image.load(full_path).convert_alpha() if convert_alpha else pygame.image.load(full_path).convert()
            if scale_factor: image = pygame.transform.scale(image,(int(image.get_width()*SCALE_FACTOR),int(image.get_height()*SCALE_FACTOR)))
            images[image_name.split(".")[0]] = image
    return images

def load(path,convert_alpha = True,scale_factor=True):
    image = pygame.image.load("assets/graphics/"+path+".png").convert_alpha() if convert_alpha else pygame.image.load("assets/graphics/"+path+".png").convert()
    if scale_factor: image = pygame.transform.scale(image,(int(image.get_width()*SCALE_FACTOR),int(image.get_height()*SCALE_FACTOR)))
    return image

def load_scale(path,scale_factor,convert_alpha = True):
    image = pygame.image.load("assets/graphics/"+path+".png").convert_alpha() if convert_alpha else pygame.image.load("assets/graphics/"+path+".png").convert()
    image = pygame.transform.scale(image,(int(image.get_width()*scale_factor),int(image.get_height()*scale_factor)))
    return image

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
            
def inside_range(number:float|int,rangeStart:float|int,rangeEnd:float|int)->bool:
    return number >= min(rangeStart,rangeEnd) and number <= max(rangeStart,rangeEnd)

def import_dict_fx(path, scale=2):
    images = import_folder_dict(path,True,False)
    final_images = {}
    for name, image in images.items():
        splitted = name.split("_")
        real_name = splitted[0:-1]
        real_str = "_".join(real_name)
        final_images[real_str] = pygame.transform.scale(image, (int(image.get_width()*scale),int(image.get_height()*scale)))
    return final_images

def lerp(start, end, t): return start * (1 - t) + end * t

def parse_items_string(string:str):
    string = string.replace("items:","")
    string = string.split(",")
    return string
        