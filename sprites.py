import pygame
from numpy import interp
from settings import *

vec = pygame.math.Vector2

class Player(pygame.sprite.Sprite):
    def __init__(self, game, side):
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.side = side
        self.load_images()
        self.image = self.action_frames["standing"][0]
        self.rect = self.image.get_rect()
        if self.side == "blue":
            self.rect.midbottom = (100, 270)
            self.pos = vec(100, 270)
        elif self.side == "green":
            self.rect.midbottom = (700, 270)
            self.pos = vec(700, 270)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.current_frame = 0
        self.last_update = 0
        self.standing = True
        self.pre_slashing = False
        self.slashing = False
        self.after_slashing = False

        self.dead_last_update = 0
        self.slash_count = 0
        self.die = False

    def load_images(self):
        self.action_frames = {}
        self.action_frames["pre_slashing"] = []
        self.action_frames["slashing"] = []
        self.action_frames["after_slashing"] = []
        self.action_frames["standing"] = []
        if self.side == "blue":
            for i in range(5):
                img = pygame.image.load(r'./blue_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                img = pygame.transform.flip(img, True, False)
                self.action_frames["pre_slashing"].append(img)
            for i in range(5,8):
                img = pygame.image.load(r'./blue_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                img = pygame.transform.flip(img, True, False)
                self.action_frames["slashing"].append(img)
            for i in range(8, 13):
                img = pygame.image.load(r'./blue_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                img = pygame.transform.flip(img, True, False)
                self.action_frames["after_slashing"].append(img)
            for i in range(13, 15):
                img = pygame.image.load(r'./blue_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                img = pygame.transform.flip(img, True, False)
                self.action_frames["standing"].append(img)
        
        elif self.side == "green":
            for i in range(5):
                img = pygame.image.load(r'./green_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                self.action_frames["pre_slashing"].append(img)
            for i in range(5,8):
                img = pygame.image.load(r'./green_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                self.action_frames["slashing"].append(img)
            for i in range(8, 13):
                img = pygame.image.load(r'./green_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                self.action_frames["after_slashing"].append(img)
            for i in range(13, 15):
                img = pygame.image.load(r'./green_rogue/{}.png'.format(i)).convert_alpha()
                rect = img.get_rect()
                img = pygame.transform.scale(img, (rect.width*2, rect.height*2))
                self.action_frames["standing"].append(img)
        self.rip_img = pygame.image.load(r'./rip.png')
        rect = self.rip_img.get_rect()
        self.rip_img = pygame.transform.scale(self.rip_img, ((rect.width // 15), (rect.height // 15)))

    def update(self):
        self.animate()
        self.acc = vec(0, PLAYER_GRAV)
        if self.pre_slashing or self.after_slashing:
            if self.side == "blue":
                self.acc.x = PLAYER_ACC
            elif self.side == 'green':
                self.acc.x = -1 * PLAYER_ACC
        
        self.acc.x += self.vel.x * PLAYER_FRICTION
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc
        if self.pos.y > 270:
            self.pos.y = 270
        self.rect.midbottom = self.pos 

    def animate(self):
        now = pygame.time.get_ticks()
        if self.standing:
            self.action("standing", 170)
        elif self.pre_slashing:
            if self.action_once("pre_slashing", 150):
                self.pre_slashing = False
                self.slashing = True
        elif self.slashing:
            self.action("slashing", 100)
        elif self.after_slashing:
            if self.action_once("after_slashing", 150):
                self.after_slashing = False
    
    def action(self, kind, rate):
        now = pygame.time.get_ticks()
        if now - self.last_update > rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.action_frames[kind])
            bottom = self.rect.bottom
            self.image = self.action_frames[kind][self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    
    def action_once(self, kind, rate):
        now = pygame.time.get_ticks()
        if now - self.last_update > rate:
            self.last_update = now
            self.current_frame = self.current_frame + 1
            if self.current_frame >= len(self.action_frames[kind]):
                # 如果整組動畫結束則回傳True
                return True
            bottom = self.rect.bottom
            self.image = self.action_frames[kind][self.current_frame]
            self.rect = self.image.get_rect()
            self.rect.bottom = bottom
    
    def dead(self, slashes):
        if not self.die:
            slash_img = self.game.slash_img
            rect = slash_img.get_rect()
            slash_img = pygame.transform.scale(slash_img, (rect.width // 2, rect.height // 2))
            rotated = pygame.transform.rotate(slash_img, slashes[self.slash_count][1])
            rect = rotated.get_rect()
            centerx = interp(slashes[self.slash_count][0][0], (0, 400), (self.rect.centerx-10, self.rect.centerx+10))
            centery = interp(slashes[self.slash_count][0][1], (0, 400), (self.rect.centery-10, self.rect.centery+10))
            rect.center = (centerx, centery)
            self.game.gameDisplay.blit(rotated, rect)
            
            now = pygame.time.get_ticks()
            if now - self.dead_last_update > 140:
                self.game.sword_swing_sound.play()
                self.dead_last_update = now
                self.slash_count += 1
                if self.slash_count >= len(slashes):
                    self.die = True
                    self.image = self.rip_img
                    self.rect = self.image.get_rect()
                    self.rect.midbottom = self.pos