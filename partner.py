import pygame
import math
import os

class Partner(pygame.sprite.Sprite):
    def __init__(self, player, sound_manager=None):
        super().__init__()
        self.player = player
        self.player_id = player.player_id
        
        self.eagle_frames = []
        for i in range(1, 5):
            path = os.path.join('assets', 'partner', 'eagle', f'eagle ({i}).png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (48, 48))
            self.eagle_frames.append(image)
            
        self.eagle_left_frames = [pygame.transform.flip(frame, True, False) 
                                for frame in self.eagle_frames]
        
        self.skull_frames = []
        for i in range(1, 5):
            path = os.path.join('assets', 'partner', 'skull', f'skull ({i}).png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (32, 32))
            self.skull_frames.append(image)
            
        self.skull_left_frames = [pygame.transform.flip(frame, True, False) 
                                for frame in self.skull_frames]
        
        self.frames = self.eagle_frames
        self.left_frames = self.eagle_left_frames
        
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        
        self.player = player
        self.angle = 0
        self.orbit_speed = 2
        self.orbit_radius = 60
        
        self.update_position()
        
        self.is_shooting = False
        self.shooting_direction = 'right'
        
        self.partner_type = "eagle"  # Default type
        self.width, self.height = 48, 48  # Default dimensions for scaling
        
        self.sound_manager = sound_manager

    def update_position(self):
        self.rect.centerx = self.player.rect.centerx + math.cos(math.radians(self.angle)) * self.orbit_radius
        self.rect.centery = self.player.rect.centery + math.sin(math.radians(self.angle)) * self.orbit_radius
        
    def animate(self, dt):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            
            if self.is_shooting:
                self.frames = self.left_frames if self.shooting_direction == 'left' else self.eagle_frames
            else:
                self.frames = self.left_frames if 'left' in self.player.facing else self.eagle_frames
                
            self.image = self.frames[self.frame_index]

    def shoot_at(self, target_pos):
        self.is_shooting = True
        self.shooting_direction = 'left' if target_pos[0] < self.rect.centerx else 'right'
        self.shooting_target = target_pos  # Store target position for projectile creation
        
        # Tambahkan panggilan suara di sini juga
        if self.sound_manager:
            print("DEBUG: Playing partner throw sound from shoot_at")
            self.sound_manager.play_random_partner_throw(self.partner_type)

    def stop_shooting(self):
        self.is_shooting = False
        
    def update(self, dt):
        # Add a check at the start of update to ensure correct frames are used
        if self.partner_type == "skull":
            self.frames = self.skull_frames
            self.left_frames = self.skull_left_frames
        else:
            self.frames = self.eagle_frames
            self.left_frames = self.eagle_left_frames
        
        self.angle = (self.angle + self.orbit_speed) % 360
        
        self.update_position()
        
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            
            # Use correct frames based on direction and shooting status
            if self.is_shooting:
                if self.shooting_direction == 'left':
                    self.image = self.left_frames[self.frame_index]
                else:
                    self.image = self.frames[self.frame_index]
            else:
                if hasattr(self.player, 'facing') and self.player.facing == 'left':
                    self.image = self.left_frames[self.frame_index]
                else:
                    self.image = self.frames[self.frame_index]
                
    def get_shooting_position(self):
        return self.rect.centerx, self.rect.centery

    def get_projectile_type(self):
        """Return the projectile type based on partner type"""
        if self.partner_type == "skull":
            return "fireball"
        else:
            return "rock"
    
    def change_type(self, new_type):
        """Change the partner type (e.g., from eagle to skull)"""
        if new_type == "skull" and self.partner_type != "skull":
            self.partner_type = "skull"
            
            # Update sprite images
            try:
                # Use the existing skull frames that are already loaded in __init__
                self.frames = self.skull_frames
                self.left_frames = self.skull_left_frames
                
                # Reset to idle state
                self.image = self.frames[0]
                self.frame_index = 0  # Reset frame index
                
                # Update width and height to match skull size
                self.width, self.height = 32, 32  # Skull dimensions
                
                return True
            except Exception as e:
                print(f"Error changing partner type: {e}")
                return False
        return False
    
    def shoot(self, target_pos):
        self.is_shooting = True
        self.shooting_direction = 'left' if target_pos[0] < self.rect.centerx else 'right'
        
        # Tambahkan panggilan suara
        if self.sound_manager:
            self.sound_manager.play_random_partner_throw(self.partner_type)