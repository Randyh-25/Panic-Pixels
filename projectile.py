# projectile.py
import pygame
import math
from settings import WIDTH, HEIGHT, GREEN

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.start_x = x
        self.start_y = y
        dx = target_x - x
        dy = target_y - y
        dist = max(math.hypot(dx, dy), 0.1)
        self.dx = dx / dist
        self.dy = dy / dist
        self.speed = 7
        self.damage = 10
        self.max_distance = 800  # Jarak maksimum proyektil dapat meluncur

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        
        # Hitung jarak yang sudah ditempuh
        distance = math.hypot(self.rect.centerx - self.start_x, 
                            self.rect.centery - self.start_y)
        
        # Hapus proyektil jika sudah melewati jarak maksimum
        if distance > self.max_distance:
            self.kill()
