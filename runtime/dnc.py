import pygame
from settings import *

@singleton
class DNC:
    def __init__(self, debug):
        self.display_surface = pygame.display.get_surface()
        self.day_counter = 1
        self.debug = debug
        self.ui_changed = False
        
        self.night_alpha = 50
        self.day_alpha = 0
        self.cur_alpha = self.day_alpha
        self.black_alpha = 0
        
        self.night_surf = pygame.Surface(WINDOW_SIZES,pygame.SRCALPHA)
        self.night_surf.fill((50,0,255))
        self.night_surf.set_alpha(self.day_alpha)
        self.black_surf = pygame.Surface(WINDOW_SIZES,pygame.SRCALPHA)
        self.black_surf.fill("black")
        self.black_surf.set_alpha(self.black_alpha)
        
        self.status = 0 # 0 = day, 1 = night
        self.in_transition = False
        self.black_transition = False
        self.start_time = pygame.time.get_ticks()
        
    def sleep(self):
        if self.status == 1: self.black_transition = True
        
    def is_day(self): return self.status == 0
    def is_night(self): return self.status == 1
    
    @runtime
    def update(self, dt):
        self.debug.updates += 1
        if self.status == 0: # day
            if self.black_transition:
                self.black_alpha -= CYCLE_TRANSITION_SPEED * 15 * dt
                if self.black_alpha <= 0: self.reset_black_0()
                self.black_surf.set_alpha(self.black_alpha)
            else:
                if self.in_transition:
                    self.cur_alpha += CYCLE_TRANSITION_SPEED* 0.2 * dt
                    if self.cur_alpha >= self.night_alpha: self.reset_transition()
                    self.night_surf.set_alpha(self.cur_alpha)
                else:
                    if pygame.time.get_ticks()-self.start_time >= DAY_DURATION: self.in_transition = True
        else:
            if self.black_transition:
                self.black_alpha += CYCLE_TRANSITION_SPEED * 15 * dt
                if self.black_alpha >= 255: self.reset_black_1()
                self.black_surf.set_alpha(self.black_alpha)
    
    @internal         
    def reset_black_0(self):
        self.black_alpha = 0
        self.black_transition = False
        self.start_time = pygame.time.get_ticks()
    @internal
    def reset_transition(self):
        self.cur_alpha = self.night_alpha
        self.status = 1
        self.in_transition = False
    @internal
    def reset_black_1(self):
        self.black_alpha = 255
        self.black_transition = True
        self.status = 0
        self.cur_alpha = 0
        self.night_surf.set_alpha(self.cur_alpha)
        self.day_counter += 1
        self.ui_changed = True
    
    @runtime
    def draw(self):
        if self.cur_alpha > 0: self.display_surface.blit(self.night_surf,(0,0)); self.debug.blits += 1
        if self.black_alpha > 0: self.display_surface.blit(self.black_surf,(0,0)); self.debug.blits += 1
        