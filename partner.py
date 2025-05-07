import pygame
import math
import os

class Partner(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        
        # Load skull animations
        self.original_frames = []  # Simpan frame original
        for i in range(1, 5):
            path = os.path.join('assets', 'partner', 'skull', f'skull ({i}).png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (32, 32))
            self.original_frames.append(image)
            
        # Buat frame untuk menghadap kiri (mirror)
        self.left_frames = [pygame.transform.flip(frame, True, False) 
                          for frame in self.original_frames]
        
        self.frames = self.original_frames  # Default menghadap kanan
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        
        # Partner movement
        self.player = player
        self.angle = 0
        self.orbit_speed = 3
        self.orbit_radius = 40
        
        # Update initial position
        self.update_position()
        
    def update_position(self):
        self.rect.centerx = self.player.rect.centerx + math.cos(math.radians(self.angle)) * self.orbit_radius
        self.rect.centery = self.player.rect.centery + math.sin(math.radians(self.angle)) * self.orbit_radius
        
    def animate(self, dt):
        # Cek arah player
        if 'left' in self.player.facing:
            self.frames = self.left_frames
        else:
            self.frames = self.original_frames
            
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            
    def update(self, dt):
        # Update rotation angle
        self.angle = (self.angle + self.orbit_speed) % 360
        
        # Update position
        self.update_position()
        
        # Update animation
        self.animate(dt)
        
    def get_shooting_position(self):
        return self.rect.centerx, self.rect.centery