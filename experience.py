import pygame
import os
from settings import YELLOW

class Experience(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.frames = []
        for i in range(9):
            path = os.path.join('assets', 'xp', f'exp{i:03d}.png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (32, 32))
            self.frames.append(image)
            
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.animation_finished = False
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def update(self):
        if not self.animation_finished:
            self.animation_timer += 1
            
            if self.animation_timer >= self.animation_speed * 60:
                self.animation_timer = 0
                
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                    self.image = self.frames[self.frame_index]
                    
                    if self.frame_index == len(self.frames) - 1:
                        self.animation_finished = True

class LevelUpEffect(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        
        self.frames = []
        for i in range(7):
            path = os.path.join('assets', 'xp', f'lvlup{i}.png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (96, 96))
            self.frames.append(image)
            
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.player = player
        self.finished = False
        
    def update(self, dt):
        self.rect.center = self.player.rect.center
        
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1
            
            if self.frame_index >= len(self.frames):
                self.finished = True
                self.kill()
            else:
                self.image = self.frames[self.frame_index]