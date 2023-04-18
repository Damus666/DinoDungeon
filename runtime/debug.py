from settings import *
import pygame
import psutil
import math

class Debug:
    def __init__(self, clock):
        self.clock = clock
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("Segoe UI",25)
        self.active = False
        
        self.top = HEIGHT//6
        self.bg_rect = pygame.Rect((0,0),(WIDTH/6,HEIGHT-self.top*2))
        self.bg_rect.midleft=(0,H_HEIGHT)
        
        self.process = psutil.Process()
        self.fps = 0
        self.better_fps = 0
        self.worse_fps = -1
        self.last_fpss = []
        self.avg_fps = 0
        self.next_avg = 0
        self.cpu = 0
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
            self.cpu = self.process.cpu_percent()
            self.ram = self.process.memory_info().rss / (1024 * 1024)
            self.dt = dt*1000
            self.session_time = pygame.time.get_ticks()/1000
        
    def update_blit(self):
        self.blit_data = []
        texts = [
            f"{self.fps:.0f} FPS",
            f"- Average: {self.avg_fps:.0f}",
            f"- MAX: {self.better_fps:.0f}",
            f"- MIN: {self.worse_fps:.0f}",
            "",
            f"RAM: {self.ram:.0f} MB",
            f"CPU: {self.cpu:.0f} %",
            "",
            f"Blitted Entities: {self.rendering}",
            f"Blits: ~{self.blits+self.rendering}",
            f"Updates: ~{self.updates}",
            f"Frame Time: {self.dt:.0f} ms",
            "",
            f"Loaded Sprites: {self.loaded_sprites}",
            f"Loaded Entities: {self.loaded_entities}",
            f"Session Time: {self.session_time:.0f} s",
            
        ]
        top = self.top+DEBUG_S
        i = 0
        for txt in texts:
            col = "white"
            if i == 0: col = CYAN; i=1
            surf = self.font.render(txt,True,col)
            rect = surf.get_rect(topleft = (DEBUG_S,top))
            top += DEBUG_SPACING
            self.blit_data.append((surf,rect))
        surf = self.font.render("Close [F3]",True,"white")
        rect = surf.get_rect(bottomleft = (DEBUG_S,self.bg_rect.bottom-DEBUG_S))
        self.blit_data.append((surf,rect))
    
    def event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
            self.active = not self.active
        
    def draw(self):
        if self.active:
            self.update_blit()
            pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_rect)
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.topleft,self.bg_rect.topright,(self.bg_rect.left,self.bg_rect.top-20)))
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.bottomleft,self.bg_rect.bottomright,(self.bg_rect.left,self.bg_rect.bottom+20)))
            for surf, rect in self.blit_data:
                self.display_surface.blit(surf,rect)
            