import pygame
from settings import *
import psutil, os

class Debug:
    def __init__(self, clock):
        self.clock = clock
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("Segoe UI",25)
        self.active = False
        
        self.top = HEIGHT//6
        self.bg_rect = pygame.Rect((0,0),(WIDTH/6,HEIGHT-self.top*2))
        self.bg_rect.midleft=(0,H_HEIGHT)
        
        self.process = psutil.Process(os.getpid())
        self.fps = 0
        self.better_fps = 0
        self.worse_fps = -1
        self.last_fpss = []
        self.avg_fps = 0
        self.next_avg = 0
        self.ram = 0
        self.loaded_sprites = 0
        self.loaded_entities = 0
        self.rendering = 0
        self.blits = 0
        self.updates = 0
        self.dt = 0
        self.session_time = 0
        self.last_check = 0
        self.check_cooldown = 1000
        self.blit_data = []
    
    @runtime
    def update(self, dt):
        if self.active:
            self.rendering = 0
            self.blits = 13
            self.updates = 4
            fps = self.clock.get_fps()
            if len(self.last_fpss) < 10: self.last_fpss.append(fps)
            else:
                self.next_avg = sum(self.last_fpss)/10
                self.last_fpss.clear()
                if self.next_avg < self.worse_fps or self.worse_fps == -1: self.worse_fps = self.next_avg
            if pygame.time.get_ticks() - self.last_check >= self.check_cooldown:
                self.fps = fps
                self.avg_fps = self.next_avg
                if self.fps > self.better_fps: self.better_fps = self.fps
                
                self.last_check = pygame.time.get_ticks()
            self.ram = self.process.memory_info().rss / (1024 * 1024)
            self.dt = dt*1000
            self.session_time = pygame.time.get_ticks()/1000
    
    @helper
    @runtime      
    def get_fps_color(self,value):return "green" if value >= 150 else "red" if value < 40 else "yellow"
    def get_updates_color(self,value):return "green" if value < 200 else "red" if value > 1000 else "yellow"
    def get_blits_color(self, value): return "green" if value < 1000 else "red" if value > 3000 else "yellow"
    
    @runtime
    def update_blit(self):
        self.blit_data = []
        texts = [
            (f"{self.fps:.0f} FPS",self.get_fps_color(self.fps)),
            (f"- Average: {self.avg_fps:.0f}",self.get_fps_color(self.avg_fps)),
            (f"- MAX: {self.better_fps:.0f}",self.get_fps_color(self.better_fps)),
            (f"- MIN: {self.worse_fps:.0f}",self.get_fps_color(self.worse_fps)),
            ("","white"),
            (f"RAM: {self.ram:.0f} MB",CYAN),
            (f"Blitted Entities: {self.rendering}",self.get_blits_color(self.rendering)),
            (f"Blits: ~{self.blits+self.rendering}",self.get_blits_color(self.blits+self.rendering)),
            (f"Updates: ~{self.updates}",self.get_updates_color(self.updates)),
            (f"Frame Time: {self.dt:.0f} ms",self.get_fps_color(self.fps)),
            ("","white"),
            (f"Loaded Sprites: {self.loaded_sprites}","white"),
            (f"Loaded Entities: {self.loaded_entities}","white"),
            (f"Session Time: {self.session_time:.0f} s","white"),
            
        ]
        top = self.top+DEBUG_S
        for txt,col in texts:
            surf = self.font.render(txt,True,col)
            rect = surf.get_rect(topleft = (DEBUG_S,top))
            top += DEBUG_SPACING
            self.blit_data.append((surf,rect))
        surf = self.font.render("Close [F3]",True,"white")
        rect = surf.get_rect(bottomleft = (DEBUG_S,self.bg_rect.bottom-DEBUG_S))
        self.blit_data.append((surf,rect))
    
    @runtime
    def event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3: self.active = not self.active
    
    @runtime
    def draw(self):
        if self.active:
            self.update_blit()
            pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_rect)
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.topleft,self.bg_rect.topright,(self.bg_rect.left,self.bg_rect.top-20)))
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.bottomleft,self.bg_rect.bottomright,(self.bg_rect.left,self.bg_rect.bottom+20)))
            for surf, rect in self.blit_data: self.display_surface.blit(surf,rect)
            