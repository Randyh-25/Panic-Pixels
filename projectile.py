import pygame
import math
from settings import WIDTH, HEIGHT, GREEN

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        
        self.speed = 7
        self.damage = 10
        self.max_distance = 800
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed

    def reset(self, start_pos, target_pos):
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        distance = math.hypot(self.rect.centerx - self.start_x, 
                            self.rect.centery - self.start_y)
        
        if distance > self.max_distance:
            self.kill()
