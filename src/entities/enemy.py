import pygame
import random
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))  # Red color for enemy
        self.rect = self.image.get_rect()
        self.spawn_enemy()

        self.speed = random.uniform(1, 3)
        self.health = 30

    def spawn_enemy(self):
        side = random.randint(0, 3)
        if side == 0:  # top
            self.rect.x = random.randint(0, 800)
            self.rect.y = -self.rect.height
        elif side == 1:  # right
            self.rect.x = 800
            self.rect.y = random.randint(0, 600)
        elif side == 2:  # bottom
            self.rect.x = random.randint(0, 800)
            self.rect.y = 600
        else:  # left
            self.rect.x = -self.rect.width
            self.rect.y = random.randint(0, 600)

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 0.1)  # Avoid division by zero
        dx, dy = dx / dist, dy / dist
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed