import pygame
from settings import *

@singleton
class Dialogue:
    def __init__(self, dungeon):
        self.display_surface = pygame.display.get_surface()
        self.dungeon = dungeon
        self.font1 = pygame.font.Font("assets/fonts/main.ttf",35)
        
        self.bg_panel = pygame.Rect(0,0,WIDTH-WIDTH/4,HEIGHT/4)
        self.panel_most_left = WIDTH/5
        self.bg_panel.bottomright = (WIDTH,HEIGHT)
        self.quit_btn = TextButton(self.bg_panel.topleft,(DIALOGUE_BTN_H,DIALOGUE_BTN_H),False,self.font1,"X")
        self.quit_btn.rect.topright = (self.bg_panel.right-DIALOGUE_OFFSET,self.bg_panel.top+DIALOGUE_OFFSET)
        
        self.name_bg_r = pygame.Rect(0,0,300,60)
        self.name_bg_r.bottomright = self.bg_panel.topright
        self.font2 = pygame.font.Font("assets/fonts/main.ttf",60)
        self.font3 = pygame.font.Font("assets/fonts/main.ttf",28)
        self.name_surf,self.name_rect = None,None
        self.visible_name_r = None
        
        self.quit()
        
    def start(self, interaction_data, name):
        self.interaction_data = interaction_data
        self.stage_data = self.interaction_data
        self.active = True
        self.name = name
        self.name_surf = self.font2.render(self.name,True,"white")
        self.name_rect = self.name_surf.get_rect(center=self.name_bg_r.center)
        self.build_stage()
    
    @internal
    def build_stage(self):
        self.texts = []
        if "text" in self.stage_data:
            last_y = DIALOGUE_OFFSET
            for i,txt in enumerate(self.stage_data["text"]):
                surf = self.font1.render(txt,True,"white"); surf.set_alpha(0)
                rect = surf.get_rect(topleft=(self.bg_panel.left+DIALOGUE_OFFSET,self.bg_panel.top+ last_y+i*5)); last_y += rect.h
                self.texts.append((surf,rect))
        self.action_btns = []
        last_left = DIALOGUE_OFFSET
        for i,action_name in enumerate(reversed(self.stage_data["actions"].keys())):
            button = TextButton((0,self.bg_panel.bottom-DIALOGUE_OFFSET-DIALOGUE_BTN_H),(100,DIALOGUE_BTN_H),False,self.font1,action_name)
            w = button.text_r.w + 20; button.rect.w = w
            button.rect.x = self.bg_panel.right-last_left-i*DIALOGUE_OFFSET-w; last_left += w
            self.action_btns.append(button)
        self.shop_btns = []
        if self.stage_data["type"] == "shop":
            x = self.bg_panel.left+50
            y = self.bg_panel.top+80
            for (item,amount),(price,price_amount) in self.stage_data["shop"]:
                button = ShopButton((x,y),(230,DIALOGUE_BTN_H),False,amount,self.dungeon.player.inventory.get_item_surf_only(item),price_amount,
                                    self.dungeon.player.inventory.get_item_surf_only(price) if price != "coins" else self.dungeon.assets["coin"]["anim"][0],
                                    self.font3,price,item)
                x += DIALOGUE_OFFSET+button.rect.w
                if x+button.rect.w >= WIDTH:
                    x = self.bg_panel.left+50
                    y += DIALOGUE_OFFSET+DIALOGUE_BTN_H
                self.shop_btns.append(button)
    
    @internal 
    def change_stage(self,name):
        stage_data = self.stage_data["actions"][name]
        if stage_data == "quit": self.quit()
        else: self.stage_data = stage_data; self.build_stage()

    @internal
    def auto_forward(self):
        if len(keys:=self.stage_data["actions"].keys()) == 1: self.change_stage(list(keys)[0])
        else:
            for action_name,value in self.stage_data["actions"].items():
                if value != "quit": self.change_stage(action_name)
            
    def quit(self):
        self.interaction_data,self.stage_data,self.active = None,None,False
        self.texts,self.action_btns,self.shop_btns = [],[],[]
        self.name = "Hero"
    
    @runtime
    def event(self,e):
        if not self.active: return
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE: self.quit(); return True
            elif e.key == pygame.K_e: self.auto_forward(); return True
        return False
    
    @runtime
    def draw(self):
        if not self.active: return
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.bg_panel,0,0)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.bg_panel.topleft,self.bg_panel.bottomleft,(self.panel_most_left,self.bg_panel.bottom)))
        
        pygame.draw.rect(self.display_surface,UI_BG_COL,self.name_bg_r)
        pygame.draw.polygon(self.display_surface,UI_BG_COL,(self.name_bg_r.topleft,self.name_bg_r.bottomleft,(self.name_bg_r.left-30,self.name_bg_r.bottom)))
        self.display_surface.blit(self.name_surf,self.name_rect)
        
        self.quit_btn.draw(self.display_surface)
        
        for txt_s,txt_r in self.texts:
            self.display_surface.blit(txt_s,txt_r)
            if (alpha:=txt_s.get_alpha()) < 255: txt_s.set_alpha(alpha+1)
            
        for btn in self.action_btns: btn.draw(self.display_surface)
        for btn in self.shop_btns: btn.draw(self.display_surface)
    
    @runtime
    def update(self, dt):
        if not self.active: return
        if self.quit_btn.check(): self.quit()
        
        for btn in self.action_btns:
            if btn.check(): self.change_stage(btn.name)
            
        for btn in self.shop_btns:
            if btn.check(): self.dungeon.player.shop_action(btn)

@internal  
class DialogueButton:
    def __init__(self,pos,size,centered=False,name=""):
        self.rect = pygame.Rect(pos,size)
        if centered: self.rect.center = pos
        self.name = name
        self.was_pressing = False
        self.hovering = False
    
    @runtime
    def check(self):
        mouse = pygame.mouse.get_pressed(); action = False
        self.hovering = self.rect.collidepoint(pygame.mouse.get_pos())
        if mouse[0]:
            if not self.was_pressing:
                self.was_pressing = True
                if self.hovering: action = True
        else: self.was_pressing = False
        return action
    
    @runtime
    def draw(self,screen):
        self.base_draw(screen)
    
    @runtime
    def base_draw(self,screen):
        if self.hovering: pygame.draw.rect(screen,(150,150,150),self.rect.inflate(4,4),0,4)
        pygame.draw.rect(screen,UI_DIALOGUE_BTN_COL,self.rect,0,4)

@internal
class TextButton(DialogueButton):
    def __init__(self, pos, size, centered, font, text):
        super().__init__(pos,size,centered,text)
        self.font = font; self.text = text
        self.text_s = self.font.render(self.text,True,"white")
        self.text_r = self.text_s.get_rect()
    
    @override
    def draw(self, screen):
        self.base_draw(screen)
        self.text_r.center = self.rect.center
        screen.blit(self.text_s,self.text_r)

@internal
class ShopButton(DialogueButton):
    def __init__(self, pos, size, centered, amount, item_img, price_amount, price_img, font:pygame.font.Font, price_name, item_name):
        super().__init__(pos,size,centered,"shop_button")
        
        self.amount = amount
        self.item_img = item_img
        self.price_amount = price_amount
        self.price_img = price_img
        self.font = font
        
        scale = 0.7
        self.item_img = pygame.transform.scale(self.item_img,(int(self.item_img.get_width()*scale),int(self.item_img.get_height()*scale)))
        if price_name != "coins":
            self.price_img = pygame.transform.scale(self.price_img,(int(self.price_img.get_width()*scale),int(self.price_img.get_height()*scale)))
        self.price_name = price_name
        self.item_name = item_name
        
        self.amount_surf = self.font.render(str(self.amount),False,"white")
        self.price_amount_surf = self.font.render(str(self.price_amount),False,"white")
        self.amount_rect = self.amount_surf.get_rect(midright=(self.rect.centerx+self.rect.width//4,self.rect.centery+2))
        self.item_rect = self.item_img.get_rect(midleft=(self.amount_rect.right,self.rect.centery))
        self.price_rect = self.price_img.get_rect(midleft=(self.rect.centerx-self.rect.width//4,self.rect.centery))
        self.price_amount_rect = self.price_amount_surf.get_rect(midright = (self.price_rect.left,self.rect.centery+2))
        
        self.arrow_surf = self.font.render("=>",False,"white")
        self.arrow_rect = self.arrow_surf.get_rect(center=self.rect.center)
        
    def draw(self, screen):
        self.base_draw(screen)
        
        screen.blit(self.amount_surf,self.amount_rect)
        screen.blit(self.item_img,self.item_rect)
        screen.blit(self.price_amount_surf,self.price_amount_rect)
        screen.blit(self.price_img,self.price_rect)
        screen.blit(self.arrow_surf,self.arrow_rect)
