import pygame
import math
import random
import os
from settings import WIDTH, HEIGHT, GREEN

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, projectile_type="rock"):
        super().__init__()
        
        self.projectile_type = projectile_type
        
        # Load rock images
        self.rock_images = []
        for i in range(3):
            path = os.path.join("assets", "projectile", "rock", f"rock{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                # Scale to appropriate size
                image = pygame.transform.scale(image, (16, 16))
                self.rock_images.append(image)
            except pygame.error as e:
                print(f"Error loading rock sprite: {path}")
                print(e)
                # Fallback to a simple surface if image loading fails
                fallback = pygame.Surface((10, 10))
                fallback.fill(GREEN)
                self.rock_images.append(fallback)
        
        # Load fireball images
        self.fireball_frames = []
        for i in range(1, 6):  # FB001.png to FB005.png
            path = os.path.join("assets", "projectile", "fireball", f"FB00{i}.png")
            try:
                original_image = pygame.image.load(path).convert_alpha()
                
                # Get original dimensions and maintain aspect ratio
                orig_width = original_image.get_width()
                orig_height = original_image.get_height()
                
                # Calculate new dimensions preserving aspect ratio
                # Use a base width of 32 pixels and scale height proportionally
                scale_factor = 32 / orig_width
                new_width = 32
                new_height = int(orig_height * scale_factor)
                
                # Scale the image with the correct aspect ratio
                image = pygame.transform.scale(original_image, (new_width, new_height))
                self.fireball_frames.append(image)
            except pygame.error as e:
                print(f"Error loading fireball sprite: {path}")
                print(e)
                # Fallback to a simple surface if image loading fails
                fallback = pygame.Surface((16, 16))
                fallback.fill((255, 0, 0))  # Red for fireball
                self.fireball_frames.append(fallback)
        
        self.fireball_frame_index = 0
        self.fireball_animation_speed = 0.15
        self.fireball_animation_timer = 0
        
        # Select image based on projectile type
        if self.projectile_type == "fireball":
            self.original_image = self.fireball_frames[0]
        else:
            # Randomly select one of the rocks
            self.original_image = random.choice(self.rock_images)
            
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        
        self.speed = 7
        self.damage = 15 if self.projectile_type == "fireball" else 10  # Fireball does more damage
        self.max_distance = 800
        self.rotation = 0
        self.rotation_speed = random.uniform(5, 15) if self.projectile_type == "rock" else 0  # No rotation for fireball
        
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed
        
        # Calculate angle for fireball direction
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # Determine rotation direction (clockwise or counter-clockwise)
        self.rotation_dir = random.choice([-1, 1])
        
        # For fireball, rotate to face direction of movement
        if self.projectile_type == "fireball":
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def reset(self, start_pos, target_pos, projectile_type="rock"):
        self.projectile_type = projectile_type
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        
        # Select image based on projectile type
        if self.projectile_type == "fireball":
            self.original_image = self.fireball_frames[0]
            self.damage = 15  # Fireball does more damage
            self.rotation_speed = 0  # No rotation for fireball
            self.fireball_frame_index = 0
            self.fireball_animation_timer = 0
        else:
            # Randomly select one of the rocks
            self.original_image = random.choice(self.rock_images)
            self.damage = 10
            self.rotation_speed = random.uniform(5, 15)
        
        self.image = self.original_image.copy()
        
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed
        
        # Calculate angle for fireball direction
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # For fireball, rotate to face direction of movement
        if self.projectile_type == "fireball":
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            
        # Reset rotation direction
        self.rotation_dir = random.choice([-1, 1])
        self.rotation = 0

    def update(self, dt=1/60):
        # Update position
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        if self.projectile_type == "fireball":
            # Update fireball animation
            self.fireball_animation_timer += dt
            if self.fireball_animation_timer >= self.fireball_animation_speed:
                self.fireball_animation_timer = 0
                self.fireball_frame_index = (self.fireball_frame_index + 1) % len(self.fireball_frames)
                self.original_image = self.fireball_frames[self.fireball_frame_index]
                
                # Maintain the rotation while updating the frame
                self.image = pygame.transform.rotate(self.original_image, -self.angle)
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center
        else:
            # Update rotation for rock
            self.rotation += self.rotation_speed * self.rotation_dir
            self.rotation %= 360  # Keep rotation angle between 0 and 360
            
            # Rotate the image
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            
            # Keep the rect centered at the same position after rotation
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
        # Check if projectile has traveled too far
        distance = math.hypot(self.rect.centerx - self.start_x, 
                            self.rect.centery - self.start_y)
        
        if distance > self.max_distance:
            self.kill()
