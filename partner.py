import pygame
import math
import os

class Partner(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        
        # Load eagle animations
        self.eagle_frames = []
        for i in range(1, 5):
            path = os.path.join('assets', 'partner', 'eagle', f'eagle ({i}).png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (48, 48))  # Slightly larger size for eagle
            self.eagle_frames.append(image)
            
        # Create flipped versions for left-facing eagle
        self.eagle_left_frames = [pygame.transform.flip(frame, True, False) 
                                for frame in self.eagle_frames]
        
        # Load skull animations (kept for future partner selection feature)
        self.skull_frames = []
        for i in range(1, 5):
            path = os.path.join('assets', 'partner', 'skull', f'skull ({i}).png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (32, 32))
            self.skull_frames.append(image)
            
        # Create flipped versions for left-facing skull
        self.skull_left_frames = [pygame.transform.flip(frame, True, False) 
                                for frame in self.skull_frames]
        
        # Set default frames to eagle
        self.frames = self.eagle_frames
        self.left_frames = self.eagle_left_frames
        
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        
        # Partner movement
        self.player = player
        self.angle = 0
        self.orbit_speed = 2  # Slightly slower for eagle
        self.orbit_radius = 60  # Larger orbit radius for eagle
        
        # Update initial position
        self.update_position()
        
    def update_position(self):
        self.rect.centerx = self.player.rect.centerx + math.cos(math.radians(self.angle)) * self.orbit_radius
        self.rect.centery = self.player.rect.centery + math.sin(math.radians(self.angle)) * self.orbit_radius
        
    def animate(self, dt):
        # Check player direction
        if 'left' in self.player.facing:
            self.frames = self.left_frames
        else:
            self.frames = self.eagle_frames
            
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