import pygame
import random

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 0, 255))  # Blue color
        self.rect = self.image.get_rect()
        self.rect.center = (400, 300)  # Starting position
        self.speed = 5
        self.health = 100
        self.score = 0
        self.weapons = []

    def add_weapon(self, weapon):
        self.weapons.append(weapon)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.rect.y += self.speed

        # Keep player on screen
        self.rect.x = max(0, min(800 - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(600 - self.rect.height, self.rect.y))