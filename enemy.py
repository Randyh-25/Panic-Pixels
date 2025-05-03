# enemy.py
import pygame
import random
import math
from settings import WIDTH, HEIGHT, RED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__()
        # Regular enemy image
        self.alive_image = pygame.Surface((20, 20))
        self.alive_image.fill(RED)
        
        # Load collapse animation frames
        self.collapse_frames = [
            pygame.image.load("assets/enemy/collapse/c0.png").convert_alpha(),
            pygame.image.load("assets/enemy/collapse/c1.png").convert_alpha(),
            pygame.image.load("assets/enemy/collapse/c2.png").convert_alpha()
        ]
        
        # Animation variables
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 5  # Frames to wait before next animation frame
        self.is_dying = False
        
        # Set initial image
        self.image = self.alive_image
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

    def start_death_animation(self):
        self.is_dying = True
        self.current_frame = 0
        self.animation_timer = 0
        self.image = self.collapse_frames[0]

    def update(self, player):
        if self.is_dying:
            # Handle death animation
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.collapse_frames):
                    self.kill()  # Remove enemy when animation is complete
                else:
                    self.image = self.collapse_frames[self.current_frame]
        else:
            # Normal enemy behavior
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            dist = max(math.hypot(dx, dy), 0.1)
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
