import pygame
import math

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((0, 255, 0))  # Green color for the projectile
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        dx = target_x - x
        dy = target_y - y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = dx / dist
        self.dy = dy / dist
        self.speed = 7
        self.damage = 10

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        # Remove if out of screen
        if (self.rect.right < 0 or self.rect.left > 800 or 
            self.rect.bottom < 0 or self.rect.top > 600):
            self.kill()