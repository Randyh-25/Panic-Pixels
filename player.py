# player.py
import pygame
from settings import WIDTH, HEIGHT, BLUE
from utils import load_game_data

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed = 5
        self.max_health = 100
        self.health = self.max_health
        self.saved_money, _, self.name = load_game_data()  # Load player data
        self.session_money = 0  # Money earned in current session
        self.xp = 0
        self.max_xp = 100
        self.level = 1
        self.world_bounds = None  # Will be set in main.py

    def update(self):
        old_x = self.rect.x
        old_y = self.rect.y
        
        # Get pressed keys and store movement
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
            
        # Try horizontal movement
        self.rect.x += dx
        if any(self.rect.colliderect(fence) for fence in self.game_map.fence_rects):
            self.rect.x = old_x
            
        # Try vertical movement
        self.rect.y += dy
        if any(self.rect.colliderect(fence) for fence in self.game_map.fence_rects):
            self.rect.y = old_y

class Camera:
    def __init__(self, map_width, map_height):
        self.x = 0
        self.y = 0
        self.map_width = map_width
        self.map_height = map_height

    def apply(self, entity):
        # Returns adjusted rectangle position for rendering
        return entity.rect.move(self.x, self.y)

    def update(self, target):
        # Center the camera on the target (usually the player)
        self.x = -target.rect.centerx + WIDTH // 2
        self.y = -target.rect.centery + HEIGHT // 2
        
        # Limit scrolling to map boundaries
        self.x = min(0, max(-(self.map_width - WIDTH), self.x))
        self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
