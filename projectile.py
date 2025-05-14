import pygame
import math
import random
import os
from settings import WIDTH, HEIGHT, GREEN

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        
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
        
        # Randomly select one of the rocks
        self.original_image = random.choice(self.rock_images)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        
        self.speed = 7
        self.damage = 10
        self.max_distance = 800
        self.rotation = 0
        self.rotation_speed = random.uniform(5, 15)  # Random rotation speed
        
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed
        
        # Determine rotation direction (clockwise or counter-clockwise)
        self.rotation_dir = random.choice([-1, 1])
    
    def reset(self, start_pos, target_pos):
        # Reset position
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        
        # Reset rotation
        self.rotation = 0
        self.rotation_speed = random.uniform(5, 15)
        self.rotation_dir = random.choice([-1, 1])
        
        # Select a new random rock
        self.original_image = random.choice(self.rock_images)
        self.image = self.original_image.copy()
        
        # Reset velocity
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed

    def update(self):
        # Update position
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # Update rotation
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
