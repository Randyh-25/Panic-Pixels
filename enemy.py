# enemy.py
import pygame
import random
import math
import os
from settings import WIDTH, HEIGHT, RED

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__()
        
        # Load walking animation frames
        self.walk_frames = []
        for i in range(8):  # Load fly0.png through fly7.png
            path = os.path.join("assets", "enemy", "fly-eye", "walk", f"fly{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                # Increase size to 96x96 (was 64x64)
                image = pygame.transform.scale(image, (128, 128))
                self.walk_frames.append(image)
            except pygame.error as e:
                print(f"Error loading enemy sprite: {path}")
                print(e)
        
        # Load hit animation frames
        self.hit_frames = []
        for i in range(4):  # Load hit0.png through hit3.png
            path = os.path.join("assets", "enemy", "fly-eye", "hit", f"hit{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                # Match the size with walk frames
                image = pygame.transform.scale(image, (128, 128))
                self.hit_frames.append(image)
            except pygame.error as e:
                print(f"Error loading hit sprite: {path}")
                print(e)
        
        # Load death animation frames
        self.death_frames = []
        for i in range(4):  # Load death0.png through death3.png
            path = os.path.join("assets", "enemy", "fly-eye", "death", f"death{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                # Match the size with walk frames
                image = pygame.transform.scale(image, (128, 128))
                self.death_frames.append(image)
            except pygame.error as e:
                print(f"Error loading death sprite: {path}")
                print(e)
        
        # Animation variables
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.animation_time = 0
        
        # State variables
        self.is_dying = False
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.2  # Duration of hit animation in seconds
        
        # Set initial image
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect()
        self.spawn(player_pos)
        self.speed = random.uniform(1, 3)
        self.health = 30
        
        # Add movement and collision variables
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.separation_radius = 60  # Increased from 40 to match new size
        
        # Sprite flipping
        self.facing_left = False

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
        self.pos = pygame.math.Vector2(self.rect.center)

    def take_hit(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.start_death_animation()
        else:
            self.start_hit_animation()

    def start_hit_animation(self):
        self.is_hit = True
        self.hit_timer = 0
        self.current_frame = 0

    def start_death_animation(self):
        self.is_dying = True
        self.current_frame = 0
        self.animation_timer = 0

    def separate_from_enemies(self, enemies):
        # Initialize separation vector
        separation = pygame.math.Vector2()
        total = 0
        
        # Check distance to each other enemy
        for enemy in enemies:
            if enemy != self:
                distance = pygame.math.Vector2(
                    self.rect.centerx - enemy.rect.centerx,
                    self.rect.centery - enemy.rect.centery
                )
                dist_length = distance.length()
                
                # If enemies are too close, calculate separation force
                if dist_length < self.separation_radius:
                    if dist_length > 0:  # Avoid division by zero
                        separation += distance.normalize() / dist_length
                    else:
                        # If exactly overlapping, push in random direction
                        angle = random.uniform(0, 2 * math.pi)
                        separation += pygame.math.Vector2(
                            math.cos(angle),
                            math.sin(angle)
                        )
                    total += 1
        
        # Apply separation force if there were nearby enemies
        if total > 0:
            separation = separation / total
            if separation.length() > 0:
                separation = separation.normalize() * self.speed
                return separation
        
        return pygame.math.Vector2()

    def animate(self, dt):
        if self.is_dying:
            # Death animation
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                if self.current_frame < len(self.death_frames) - 1:
                    self.current_frame += 1
                    self.image = self.death_frames[self.current_frame]
                    if self.facing_left:
                        self.image = pygame.transform.flip(self.image, True, False)
                elif self.current_frame >= len(self.death_frames) - 1:
                    self.kill()
        
        elif self.is_hit:
            # Hit animation
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.current_frame = 0
            else:
                frame_index = int((self.hit_timer / self.hit_duration) * len(self.hit_frames))
                frame_index = min(frame_index, len(self.hit_frames) - 1)
                self.image = self.hit_frames[frame_index]
                if self.facing_left:
                    self.image = pygame.transform.flip(self.image, True, False)
        
        else:
            # Walking animation
            self.animation_time += dt
            if self.animation_time >= self.animation_speed:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                self.image = self.walk_frames[self.current_frame]
                if self.facing_left:
                    self.image = pygame.transform.flip(self.image, True, False)

    def update(self, player, enemies=None):
        if self.is_dying:
            self.animate(1/60)
            return
            
        # Calculate direction to player
        to_player = pygame.math.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )
        
        # Update facing direction
        if to_player.x != 0:
            self.facing_left = to_player.x < 0
        
        # Only move if not in hit animation
        if not self.is_hit:
            if to_player.length() > 0:
                to_player = to_player.normalize() * self.speed
            
            # Apply separation from other enemies
            separation = pygame.math.Vector2()
            if enemies:
                separation = self.separate_from_enemies(enemies)
            
            # Combine movement vectors
            final_movement = to_player + separation
            
            # Normalize final movement if it exceeds speed
            if final_movement.length() > self.speed:
                final_movement = final_movement.normalize() * self.speed
            
            # Update position
            self.pos += final_movement
            self.rect.center = self.pos
        
        # Update animation
        self.animate(1/60)
