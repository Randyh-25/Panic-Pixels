# enemy.py
import pygame
import random
import math
from settings import WIDTH, HEIGHT, RED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.spawn(player_pos)
        self.speed = random.uniform(1, 3)
        self.health = 30

    def spawn(self, player_pos):
        # Jarak spawn dari pemain
        spawn_distance = 400  # Jarak minimal spawn dari pemain
        
        # Pilih sudut random untuk spawn
        angle = random.uniform(0, 2 * math.pi)
        
        # Hitung posisi spawn relatif terhadap pemain
        spawn_x = player_pos[0] + math.cos(angle) * spawn_distance
        spawn_y = player_pos[1] + math.sin(angle) * spawn_distance
        
        self.rect.x = spawn_x
        self.rect.y = spawn_y

    def update(self, player):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = max(math.hypot(dx, dy), 0.1)
        self.rect.x += (dx / dist) * self.speed
        self.rect.y += (dy / dist) * self.speed
