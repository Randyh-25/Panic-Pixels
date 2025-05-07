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
        
        # Tambahkan variabel untuk tracking status menembak
        self.is_shooting = False
        self.shooting_direction = 'right'  # Default shooting direction
        
    def update_position(self):
        self.rect.centerx = self.player.rect.centerx + math.cos(math.radians(self.angle)) * self.orbit_radius
        self.rect.centery = self.player.rect.centery + math.sin(math.radians(self.angle)) * self.orbit_radius
        
    def animate(self, dt):
        # Update animation timer
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            
            # Select appropriate frames based on shooting status and direction
            if self.is_shooting:
                # Use shooting direction while shooting
                self.frames = self.left_frames if self.shooting_direction == 'left' else self.eagle_frames
            else:
                # Follow player direction when not shooting
                self.frames = self.left_frames if 'left' in self.player.facing else self.eagle_frames
                
            self.image = self.frames[self.frame_index]

    def shoot_at(self, target_pos):
        # Determine shooting direction based on target position
        self.is_shooting = True
        self.shooting_direction = 'left' if target_pos[0] < self.rect.centerx else 'right'
        
    def stop_shooting(self):
        self.is_shooting = False
        
    def update(self, dt):
        # Update rotation angle
        self.angle = (self.angle + self.orbit_speed) % 360
        
        # Update position
        self.update_position()
        
        # Update animation
        self.animate(dt)
        
    def get_shooting_position(self):
        return self.rect.centerx, self.rect.centery