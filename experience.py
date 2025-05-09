# experience.py
import pygame
import os
from settings import YELLOW

class Experience(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Load animation frames
        self.frames = []
        for i in range(9):  # Load 9 frames (000-008)
            path = os.path.join('assets', 'xp', f'exp{i:03d}.png')
            image = pygame.image.load(path).convert_alpha()
            # Scale image if needed (adjust size as needed)
            image = pygame.transform.scale(image, (32, 32))
            self.frames.append(image)
            
        # Animation settings
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # Ubah ke 0.15 untuk animasi lebih halus
        self.animation_finished = False
        
        # Set initial image
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
    def update(self):
        if not self.animation_finished:
            # Update animation timer
            self.animation_timer += 1
            
            # Update frame if enough time has passed
            if self.animation_timer >= self.animation_speed * 60:  # Convert to frames
                self.animation_timer = 0
                
                # Move to next frame
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                    self.image = self.frames[self.frame_index]
                    
                    # Check if we've reached the last frame
                    if self.frame_index == len(self.frames) - 1:
                        self.animation_finished = True

class LevelUpEffect(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        # Load level up aura animations
        self.frames = []
        for i in range(7):  # lvlup0.png to lvlup6.png
            path = os.path.join('assets', 'xp', f'lvlup{i}.png')
            image = pygame.image.load(path).convert_alpha()
            # Scale image to fit player (adjust size as needed)
            image = pygame.transform.scale(image, (96, 96))  # Slightly larger than player
            self.frames.append(image)
            
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.player = player
        self.finished = False
        
    def update(self, dt):
        # Center on player
        self.rect.center = self.player.rect.center
        
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1
            
            # Check if animation is complete
            if self.frame_index >= len(self.frames):
                self.finished = True
                self.kill()
            else:
                self.image = self.frames[self.frame_index]