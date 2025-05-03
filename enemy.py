# enemy.py
import pygame
import random
import math
from settings import WIDTH, HEIGHT, RED

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn()
        self.speed = random.uniform(1, 3)
        self.health = 30

    def spawn(self):
        side = random.randint(0, 3)
        if side == 0:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = -self.rect.height
        elif side == 1:
            self.rect.x = WIDTH
            self.rect.y = random.randint(0, HEIGHT)
        elif side == 2:
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT
        else:
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, HEIGHT)

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 0.1)
        self.rect.x += (dx / dist) * self.speed
        self.rect.y += (dy / dist) * self.speed
