import pygame, math
from settings import *
from support import *
from sprites.sprites import FloatingUI

class UIState:
    def __init__(self, debug):
        self.display_surface = pygame.display.get_surface()
        self.debug = debug
    
    def draw(self): pass
    
class UIDNC(UIState):
    def __init__(self, assets, day_night, debug):
        super().__init__(debug)
        self.day_night = day_night
        
        self.dnc_bg_rect = pygame.Rect(0,0,150,80)
        self.dnc_bg_rect.topright = (WIDTH,0)
        self.dnc_font1 = pygame.font.Font("assets/fonts/main.ttf",50)
        self.dnc_time_h = 27
        self.dnc_time_surf = pygame.Surface((130,25))
        self.dnc_time_rect = self.dnc_time_surf.get_rect(topright=(WIDTH-5,10))
        dncscale = 0.6; self.dnc_sun = pygame.transform.scale(assets["sun"],(int(TILE_SIZE*dncscale),int(TILE_SIZE*dncscale)))
        dncscale = 0.5; self.dnc_moon = pygame.transform.scale(assets["moon"],(int(TILE_SIZE*dncscale),int(TILE_SIZE*dncscale)))
        self.dnc_lil_moon = pygame.transform.scale(self.dnc_moon,(int(self.dnc_moon.get_width()*0.68),int(self.dnc_moon.get_height()*0.68)))
        dnc_img_pos = (self.dnc_time_rect.left-8,self.dnc_time_rect.centery)
        self.dnc_sun_r, self.dnc_moon_r = self.dnc_sun.get_rect(midright=dnc_img_pos), self.dnc_moon.get_rect(midright=dnc_img_pos)
        self.dnc_lil_moon_r = self.dnc_lil_moon.get_rect(topleft=self.dnc_sun_r.center)
        self.dnc_timepos_r = pygame.Rect(0,0,4,self.dnc_time_rect.h+6)
        self.dnc_timepos_r.centery = self.dnc_time_rect.centery
        self.dnc_timepos_inf = self.dnc_timepos_r.inflate(4,4)
        self.form_dnc_gradient()
        self.update_dnc()
        
    def update_dnc(self):
        self.day_count_surf = self.dnc_font1.render(f"DAY  {self.day_night.day_counter}",True,"white")
        self.day_count_rect = self.day_count_surf.get_rect(topright = (WIDTH-5,5+self.dnc_time_h))
        self.day_night.ui_changed = False
        self.debug.updates += 1
        
    def draw(self):
        # update
        if self.day_night.ui_changed: self.update_dnc()
        # time bar
        if self.day_night.status == 0 and not self.day_night.in_transition:
            if not self.day_night.black_transition:
                ratio = (pygame.time.get_ticks()-self.day_night.start_time)/DAY_DURATION; w = self.dnc_time_rect.w*ratio
                self.dnc_timepos_r.centerx = self.dnc_time_rect.left + w; self.dnc_timepos_inf.centerx = self.dnc_timepos_r.centerx
            else: self.dnc_timepos_r.centerx = self.dnc_time_rect.left; self.dnc_timepos_inf.centerx = self.dnc_timepos_r.centerx
        else: self.dnc_timepos_r.centerx = self.dnc_time_rect.right; self.dnc_timepos_inf.centerx = self.dnc_timepos_r.centerx
        # choose sun, moon
        also_t = False
        if self.day_night.status == 0:
            if self.day_night.in_transition: also_t = True
            img_touse, r_touse = self.dnc_sun,self.dnc_sun_r
        else: img_touse, r_touse = self.dnc_moon,self.dnc_moon_r
        # draw bg
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.dnc_bg_rect)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,[ (self.dnc_bg_rect.x-85,self.dnc_bg_rect.y), self.dnc_bg_rect.topleft, self.dnc_bg_rect.bottomleft])
        # draw gradient, count, sun/moon, lil moon
        self.display_surface.blit(self.dnc_time_surf,self.dnc_time_rect)
        self.display_surface.blit(self.day_count_surf,self.day_count_rect)
        self.display_surface.blit(img_touse,r_touse)
        if also_t: self.display_surface.blit(self.dnc_lil_moon,self.dnc_lil_moon_r); self.debug.blits += 1
        # draw time bar
        pygame.draw.rect(self.display_surface,"white",self.dnc_timepos_inf)
        pygame.draw.rect(self.display_surface,"red",self.dnc_timepos_r)
        self.debug.blits += 8
        
    @extend(__init__)
    def form_dnc_gradient(self):
        pixels = pygame.PixelArray(self.dnc_time_surf)
        color1 = (255, 150, 0); color2 = (0, 0, 100)
        for x in range(self.dnc_time_surf.get_width()):
            color = (
                int((color2[0] - color1[0]) * (x / self.dnc_time_surf.get_width())) + color1[0],
                int((color2[1] - color1[1]) * (x / self.dnc_time_surf.get_width())) + color1[1],
                int((color2[2] - color1[2]) * (x / self.dnc_time_surf.get_width())) + color1[2],
            )
            for y in range(self.dnc_time_surf.get_height()): pixels[x][y] = color
        del pixels
        
class UIHealth(UIState):
    def __init__(self, assets, stats, debug,bg_bottom=60):
        super().__init__(debug)
        self.stats = stats
        
        self.heart_empty = assets["ui_heart_empty"]
        self.heart_full = assets["ui_heart_full"]
        self.heart_half = assets["ui_heart_half"]
        self.heart_empty, self.heart_full, self.heart_half = pygame.transform.scale(self.heart_empty,(UI_HEART_SIZE,UI_HEART_SIZE)),\
            pygame.transform.scale(self.heart_full,(UI_HEART_SIZE,UI_HEART_SIZE)),\
            pygame.transform.scale(self.heart_half,(UI_HEART_SIZE,UI_HEART_SIZE))
        self.heart_spacing = UI_SPACING/2
        self.range_5 = range(7)
        self.hearts_bg_r = pygame.Rect(0,0,300,bg_bottom)
        
    def draw(self):
        # draw bg
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.hearts_bg_r)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.hearts_bg_r.topright,self.hearts_bg_r.bottomright,(self.hearts_bg_r.right+40,0)))
        self.debug.blits += 2
        # empty hearts
        for i in self.range_5:
            self.display_surface.blit(self.heart_empty,(self.heart_spacing+(-self.heart_spacing/2)*(i)+UI_HEART_SIZE*i,self.heart_spacing))
            self.debug.blits += 1
        # fill hearts
        last_i = 0
        for i in range(self.stats.health //2):
            self.display_surface.blit(self.heart_full,(self.heart_spacing+(-self.heart_spacing/2)*(i)+UI_HEART_SIZE*i,self.heart_spacing/2))
            last_i = i+1
            self.debug.blits += 1
        # half heart
        if self.stats.health % 2 != 0:
            self.debug.blits += 1
            self.display_surface.blit(self.heart_half,(self.heart_spacing+(-self.heart_spacing/2)*(last_i)+UI_HEART_SIZE*last_i,self.heart_spacing/2))
                  
class UICoinsSouls(UIState):
    def __init__(self, inventory, coin_img,debug, soul_img, bg_bottom=60):
        super().__init__(debug)
        self.inventory = inventory
        
        self.coins_bg_r = pygame.Rect(0,bg_bottom,120,35*2)
        cs = 1.5
        self.coin_img = pygame.transform.scale(coin_img,(int(coin_img.get_width()*cs),int(coin_img.get_height()*cs)))
        self.soul_img = pygame.transform.scale_by(soul_img,2.1)
        self.coin_rect = self.coin_img.get_rect(topleft=(self.coins_bg_r.left-2,self.coins_bg_r.top-16))
        self.soul_rect = self.soul_img.get_rect(topleft=(self.coins_bg_r.left+7,self.coins_bg_r.top-3+32))
        self.coins_font = pygame.font.Font("assets/fonts/main.ttf",40)
        self.update_things()
        
        self.floating_img = pygame.transform.scale(self.coin_img,(int(self.coin_img.get_width()*0.8),int(self.coin_img.get_height()*0.8)))
        self.floating_coins = pygame.sprite.Group()
        self.inventory.add_floating_coin = self.add_floating_coin
        self.floating_end_rect = pygame.Rect(0,bg_bottom,self.coins_bg_r.w,self.coins_bg_r.h)
    
    @external
    def add_floating_coin(self):
        self.floating_coins.add(FloatingUI(self.floating_end_rect,self.floating_img,self.debug))
    
    @runtime
    def update(self, dt):
        self.floating_coins.update(dt)
        self.debug.updates += 1
    
    @override
    def draw(self):
        # draw bg
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.coins_bg_r)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.coins_bg_r.topright,self.coins_bg_r.bottomright,(self.coins_bg_r.right+30,self.coins_bg_r.top)))
        # update
        if self.inventory.ui_changed: self.update_things()
        # draw coin, count
        self.display_surface.blit(self.coin_img,self.coin_rect)
        self.display_surface.blit(self.coin_amount_surf,self.coin_amount_rect)
        self.display_surface.blit(self.soul_img, self.soul_rect)
        self.display_surface.blit(self.soul_amount_surf,self.soul_amount_rect)
        # floating
        self.floating_coins.draw(self.display_surface)
        self.debug.blits += 5
        
    def update_things(self):
        self.coin_amount_surf = self.coins_font.render(f"{self.inventory.coins}",True,"white")
        self.coin_amount_rect = self.coin_amount_surf.get_rect(topleft=(self.coin_rect.right+3,0))
        self.coin_amount_rect.centery = self.coin_rect.centery+4
        self.soul_amount_surf = self.coins_font.render(f"{self.inventory.souls}",True,CYAN)
        self.soul_amount_rect = self.soul_amount_surf.get_rect(topleft=(self.soul_rect.right+9,0))
        self.soul_amount_rect.centery = self.soul_rect.centery
        self.inventory.ui_changed = False
        
class UIInventory(UIState):
    def __init__(self, inventory, player):
        super().__init__(player.debug)
        self.inventory = inventory
        self.player = player
        self.inventory.add_floating_item = self.add_floating_item
        
        self.bg_rect = pygame.Rect(0,0,320,72)
        self.bg_rect.centerx = WIDTH//2
        self.poly_offset = 40
        
        middle_slot = pygame.Rect(H_WIDTH-H_SLOT_SIZE,UI_SLOT_SPACING,UI_SLOT_SIZE,UI_SLOT_SIZE)
        rects = [middle_slot]
        for i in range(1,3):
            rect = middle_slot.copy()
            rect.x += UI_SLOT_SPACING*i+UI_SLOT_SIZE*i
            lrect = middle_slot.copy()
            lrect.x -= UI_SLOT_SPACING*i+UI_SLOT_SIZE*i
            rects.append(rect); rects.append(lrect)
            
        rects = sorted(rects,key=lambda r: r.centerx)
        self.slot_rects = [CornerRect(rect,UI_CORNER_W,UI_SLOT_BG_COL) for rect in rects]
        self.slot_numhints = []
        smallerfont = pygame.font.Font("assets/fonts/main.ttf",20)
        for i,slot_r in enumerate(self.slot_rects):
            hsurf = smallerfont.render(str(i+1),True,"white")
            hrect = hsurf.get_rect(center=(slot_r.original.left+5,slot_r.original.top+5))
            hrad = hsurf.get_height()//2.7
            self.slot_numhints.append((hsurf,hrect,hrad))
        self.selected_slot_rects = [CornerRect(rect,UI_CORNER_W,SLOT_SELECTED_COL) for rect in rects]
        
        self.item_font = pygame.font.Font("assets/fonts/main.ttf",30)
        
        self.floating_items = pygame.sprite.Group()
        self.floating_end_rect = self.bg_rect
    
    @external
    def add_floating_item(self, name):
        surf = self.inventory.get_item_surf_only(name)
        w,h = surf.get_size(); scale = DROP_SCALE
        surf = pygame.transform.scale(surf,(int(w*scale),int(h*scale)))
        self.floating_items.add(FloatingUI(self.floating_end_rect,surf,self.debug,True))
    
    @runtime
    def update(self, dt):
        self.floating_items.update(dt)
        self.debug.updates += 1
    
    @override
    def draw(self):
        pos = pygame.mouse.get_pos()
        # bg
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_rect)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.bottomleft,self.bg_rect.topleft,(self.bg_rect.left-self.poly_offset,self.bg_rect.top)))
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.bottomright,self.bg_rect.topright,(self.bg_rect.right+self.poly_offset,self.bg_rect.top)))
        # slots
        for i,slot_r in enumerate(self.slot_rects):
            slot = self.inventory.slots[i]
            numhint = self.slot_numhints[i]
            slot_r.draw(self.debug) if (slot.item is None or slot.item.name != self.inventory.weapon) else self.selected_slot_rects[i].draw(self.debug)
            if not slot.is_empty():
                surf,r = self.inventory.get_item_surf(slot.item.name)
                r.center = slot_r.center
                self.display_surface.blit(surf,r)
                if slot_r.original.collidepoint(pos):
                    txt = f"{slot.item.name}  |  Drop [Q]"
                    name_surf = self.item_font.render(txt,False,"white")
                    name_rect = name_surf.get_rect(midtop=(slot_r.center[0],self.bg_rect.bottom+UI_SLOT_SPACING))
                    if self.inventory.weapon != STAFF_NAME:
                        pygame.draw.rect(self.display_surface,UI_BG_COL,name_rect.inflate(10,0),0,4)
                        self.display_surface.blit(name_surf,name_rect)
                        self.debug.blits += 2
                    if self.player.key_data["q"]: self.drop_item(slot.item)
                    if slot.item and (slot.item.name in CAN_CONSUME or slot.item.name in CAN_EQUIP) and self.inventory.weapon != STAFF_NAME:
                        txt = "Equip [F]" if slot.item.name in CAN_EQUIP else "Consume [F]"
                        surf = self.item_font.render(txt,False,"white")
                        rect = surf.get_rect(midtop = (name_rect.centerx,name_rect.bottom+2))
                        pygame.draw.rect(self.display_surface,UI_BG_COL,rect.inflate(10,0),0,4)
                        self.display_surface.blit(surf,rect)
                        if self.player.key_data["f"]: self.item_interact(slot.item)
                        self.debug.blits += 2
                if slot.amount > 1:
                    amount_surf = self.item_font.render(str(slot.amount),False,"white")
                    amount_rect = amount_surf.get_rect(center=slot_r.original.midbottom)
                    pygame.draw.circle(self.display_surface,UI_BG_COL,amount_rect.center,amount_surf.get_height()//2.45)
                    self.display_surface.blit(amount_surf,amount_rect)
                    self.debug.blits += 1
                self.debug.blits += 1
            pygame.draw.circle(self.display_surface,UI_SLOT_BG_COL,numhint[1].center,numhint[2])
            self.display_surface.blit(numhint[0],numhint[1])
            self.debug.blits += 2
            
        # items
        self.floating_items.draw(self.display_surface)
        self.debug.blits += 3+len(self.floating_items.sprites())
    
    @internal
    def drop_item(self, item): self.player.drop_item(item)
    def item_interact(self, item): self.player.item_interact(item)
        
class UIOverlay(UIState):
    def __init__(self, ui_assets, debug):
        super().__init__(debug)

class UIBoss(UIState):
    def __init__(self, debug):
        super().__init__(debug)
        self.current_boss = None
        self.font = pygame.font.Font("assets/fonts/main.ttf",50)
        
        self.should_disappear = False
        self.disappear_time = 3000
        self.defeat_time = 0
        
        bar_rect = pygame.Rect(0,0,500,20)
        bar_rect.midbottom = (H_WIDTH,HEIGHT-10)
        self.health_bar = HealthBar(bar_rect,HEALTH_BAR_COL,5,True,HEALTH_OUTLINE_COL)
        self.bg_rect = pygame.Rect(0,0,520,45)
        self.bg_rect.midbottom = (H_WIDTH,HEIGHT)
        
    def start(self, boss, name=None):
        self.current_boss = boss
        self.name_surf = self.font.render(boss.name if not name else name,True,"white")
        self.name_bg_r = pygame.Rect(0,0,self.name_surf.get_width()+20,self.name_surf.get_height()-15)
        self.name_bg_r.midbottom = self.bg_rect.midtop
        self.name_rect = self.name_surf.get_rect(center=self.name_bg_r.center)
        
    def end(self):
        self.start(self.current_boss,"DEFEATED")
        self.defeat_time = pygame.time.get_ticks()
        self.should_disappear = True
        
    def end_fr(self):
        self.should_disappear = False
        self.current_boss = None
        
    def draw(self):
        if self.current_boss:
            pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_rect)
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(
                self.bg_rect.topleft,self.bg_rect.bottomleft,(self.bg_rect.left-20,self.bg_rect.bottom) ))
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(
                self.bg_rect.topright,self.bg_rect.bottomright,(self.bg_rect.right+20,self.bg_rect.bottom) ))
            self.health_bar.draw(self.current_boss.health,self.current_boss.max_health)
            pygame.draw.rect(self.display_surface,UI_BG_COL,self.name_bg_r)
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(
                self.name_bg_r.topleft,self.name_bg_r.bottomleft,(self.name_bg_r.left-20,self.name_bg_r.bottom) ))
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(
                self.name_bg_r.topright,self.name_bg_r.bottomright,(self.name_bg_r.right+20,self.name_bg_r.bottom) ))
            self.display_surface.blit(self.name_surf,self.name_rect)
            self.debug.blits += 8
            if self.should_disappear:
                if pygame.time.get_ticks()-self.defeat_time >= self.disappear_time: self.end_fr()

class UIWeapon(UIState):
    def __init__(self, player):
        super().__init__(player.debug)
        self.player = player
        self.inventory = self.player.inventory
        self.weapon_original_s = None
        self.weapon_surf, self.weapon_rect = None, None
        self.center = vector(H_WIDTH,H_HEIGHT)
        o = TILE_SIZE//4
        self.offset_r, self.offset_l = vector(o,TILE_SIZE//2+TILE_SIZE//8), vector(-o,TILE_SIZE//2+TILE_SIZE//8)
        self.mul = TILE_SIZE//2
        
        self.attacking, self.attack_speed = False, 200
        self.angle, self.next_angle = 0, 0
        
        self.font = pygame.font.Font("assets/fonts/main.ttf",50)
        
    def change_weapon(self, surf):
        self.weapon_original_s = pygame.transform.scale_by(surf,1.2)
        
    def start_attack(self, speed, fov):
        direction = vector(pygame.mouse.get_pos())-self.center
        if direction.magnitude() != 0: direction.normalize_ip()
        center = self.center+(self.offset_r if self.player.orientation == "right" else self.offset_l)+direction*self.mul
        angle = math.degrees(math.atan2(-direction.y,direction.x))-90
        self.weapon_surf = pygame.transform.rotate(self.weapon_original_s,angle)
        self.weapon_rect = self.weapon_surf.get_rect(center=center)
        self.angle = angle-fov/2
        self.next_angle = self.angle+fov
        self.attacking, self.attack_speed = True, speed
        
    def update(self, dt):
        if not self.attacking: return
        direction = angle_to_vec(self.angle+90)
        center = self.center+(self.offset_r if self.player.orientation == "right" else self.offset_l)+direction*self.mul
        self.weapon_surf = pygame.transform.rotate(self.weapon_original_s,self.angle)
        self.weapon_rect = self.weapon_surf.get_rect(center=center)
        self.angle+=self.attack_speed*dt
        if self.angle >= self.next_angle:
            self.attacking = False
            self.player.finish_attack(self.weapon_rect,(self.offset_r if self.player.orientation == "right" else self.offset_l)+direction*self.mul)
        
    def draw(self):
        if self.attacking:
            self.display_surface.blit(self.weapon_surf,self.weapon_rect)
            self.debug.blits += 1

class UIEnergy(UIState):
    def __init__(self, player, assets):
        super().__init__(player.debug)
        
        self.stats = player.stats
        self.bg_rect = pygame.Rect(0,0,360,35)
        self.bg_rect.topright = (WIDTH,0)
        rect = self.bg_rect.inflate(-20,-25)
        self.zap_img = assets["zap"]
        self.zap_rect = self.zap_img.get_rect(center=rect.midright)
        self.energy_bar = HealthBar(rect,ENERGY_COL,S_CORNER_W,True,ENERGY_OUTLINE_COL)
        self.zap_radius = self.zap_img.get_width()
        
    def draw(self):
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_rect)
        self.energy_bar.draw(self.stats.energy,self.stats.max_energy)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.topleft,self.bg_rect.bottomleft,(self.bg_rect.left-10,self.bg_rect.top)))
        pygame.draw.circle(self.display_surface,UI_BG_COL,self.zap_rect.center,self.zap_radius)
        self.display_surface.blit(self.zap_img,self.zap_rect)
        self.debug.blits += 5
        
class UIEffects(UIState):
    def __init__(self, player, assets, ui_assets):
        super().__init__(player.debug)
        self.assets = only_sprites_from_tuple(parse_sprites_ratio(assets,30))
        self.clock = pygame.transform.scale_by(ui_assets["clock"],1.25); self.clock_w = self.clock.get_width()
        self.inventory = player.inventory
        self.font = pygame.font.Font("assets/fonts/main.ttf",30)
        
        self.bg_rect = pygame.Rect(0,0,120,0); self.bg_rect.topright = (WIDTH,32)
        self.effect_h = 50
        
    def draw(self):
        items = self.inventory.effects.items()
        self.bg_rect.h = self.effect_h*len(items); h = self.bg_rect.top+5
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_rect)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_rect.topleft,self.bg_rect.bottomleft,(self.bg_rect.left-30,self.bg_rect.top)))
        self.debug.blits += 2
        for name,data in items:
            time_left = (data["duration"]-(pygame.time.get_ticks()-data["start"]))//1000
            time_surf = self.font.render(str(time_left),True,"white"); time_rect = time_surf.get_rect(topright=(self.bg_rect.right-20-self.clock_w,h))
            clock_rect = self.clock.get_rect(midleft=(time_rect.right+10,time_rect.centery))
            icon_surf = self.assets[name]; icon_rect = icon_surf.get_rect(center = (self.bg_rect.left+25,time_rect.centery))
            self.display_surface.blit(time_surf,time_rect); self.display_surface.blit(icon_surf,icon_rect)
            self.display_surface.blit(self.clock,clock_rect)
            self.debug.blits += 3; h += self.effect_h
            if "Resistance" in name: pygame.draw.line(self.display_surface,RED,icon_rect.bottomleft,icon_rect.topright,3); self.debug.blits += 1

class UIRunes(UIState):
    def __init__(self, player, assets):
        super().__init__(player.debug)
        self.inventory = player.inventory
        self.rune_imgs = [pygame.transform.scale_by(surf,0.8) for surf in [self.inventory.get_item_surf_only(rune) for rune in RUNES]]
        self.rune_rects = [rune.get_rect() for rune in self.rune_imgs]
        self.alpha_rune_imgs = [img.copy() for img in self.rune_imgs]
        [img.set_alpha(50) for img in self.alpha_rune_imgs]
        self.soul_img = pygame.transform.scale_by(assets["soul"],0.8)
        self.selected_rects:list[CornerRect] = []
        self.power_names = POWERS
        self.power_costs = [str(data["cost"]) for data in POWERS_DATA.values()]
        self.font = pygame.font.Font("assets/fonts/main.ttf",25)
        top = 72
        slot_w = 54
        inner_w = 40
        spacing = 5
        self.bg = pygame.Rect(0,0,slot_w*4+spacing*6,slot_w+4)
        self.bg.midtop = (H_WIDTH,top)
        self.left = H_WIDTH-320//2
        self.right = H_WIDTH+320//2
        x = self.bg.left+spacing
        for i in range(4):
            rect = pygame.Rect(x,self.bg.top-2,slot_w,self.bg.height-6)
            x += spacing+slot_w
            crect = CornerRect(rect,S_CORNER_W,SELECTED_POW_COL)
            self.selected_rects.append(crect)
            self.rune_rects[i].center = rect.center
        
    def draw(self):
        if self.inventory.weapon == STAFF_NAME:
            pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg)
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg.topleft,self.bg.bottomleft,(self.left,self.bg.top)))
            pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg.topright,self.bg.bottomright,(self.right,self.bg.top)))
            self.debug.blits += 3
            for i, name in enumerate(self.power_names):
                sel_r = self.selected_rects[i]
                rect = self.rune_rects[i]
                img = self.rune_imgs[i] if name in self.inventory.powers else self.alpha_rune_imgs[i]
                if self.inventory.power == name:
                    sel_r.draw(self.debug)
                    csurf = self.font.render(self.power_costs[i],True,"white")
                    crect = csurf.get_rect(midtop = (sel_r.original.centerx-self.soul_img.get_width()//2,self.bg.bottom-2))
                    soulr = self.soul_img.get_rect(midleft=(crect.right+2,crect.centery))
                    scaled = crect.inflate(38,-4)
                    scaled.midright = (soulr.right+10,soulr.centery)
                    pygame.draw.rect(self.display_surface,UI_BG_COL,scaled)
                    pygame.draw.polygon(self.display_surface,UI_BG_COL,(scaled.topleft,scaled.bottomleft,(scaled.left-8,scaled.top)))
                    pygame.draw.polygon(self.display_surface,UI_BG_COL,(scaled.topright,scaled.bottomright,(scaled.right+8,scaled.top)))
                    self.display_surface.blit(self.soul_img,soulr)
                    self.display_surface.blit(csurf,crect)
                    self.debug.blits += 5
                self.display_surface.blit(img,rect)
                self.debug.blits += 1
      