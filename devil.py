import pygame
import os
import random
import math

DEVIL_SIZE = (256, 256)
DAMAGE_CIRCLE_RADIUS = 180  # Radius for damage circle

class Devil(pygame.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super().__init__()
        # Idle anim
        self.idle_frames = []
        for i in range(1, 8):
            path = os.path.join("assets", "devil", "idle", f"idle ({i}).png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, DEVIL_SIZE)
            self.idle_frames.append(img)

        # Guard anim
        self.guard_frames = []
        for i in range(1, 14):
            path = os.path.join("assets", "devil", "guard", f"guard ({i}).png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, DEVIL_SIZE)
            self.guard_frames.append(img)

        # Spawn/despawn anim
        self.spawn_frames = []
        for i in range(1, 10):
            path = os.path.join("assets", "devil", "spawn", f"spawn ({i}).png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, DEVIL_SIZE)
            self.spawn_frames.append(img)

        # Shadow
        self.shadow_img = pygame.image.load(os.path.join("assets", "shadow.png")).convert_alpha()
        self.shadow_img = pygame.transform.scale(self.shadow_img, (DEVIL_SIZE[0], DEVIL_SIZE[1] // 3))

        # Circle damage area - now repurposed for shop interaction
        self.damage_circle_radius = DAMAGE_CIRCLE_RADIUS
        self.damage_circle_color = (255, 0, 0, 80)  # Semi-transparent red
        self.damage_circle_active = False
        
        # New: Interaction properties
        self.is_player_in_range = False
        self.is_shop_enabled = True  # Devil is now a shopkeeper

        self.frame_idx = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.guard_idx = 0
        self.guard_timer = 0
        self.guard_speed = 0.08
        
        # Flag to track if guard animation has completed
        self.guard_completed = False

        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.spawn_random(map_width, map_height)

        # --- Guard/Idle switching ---
        self.state = "idle"  # idle, guard, despawn
        self.state_timer = 0
        self.guard_duration = 5  # detik
        self.idle_duration = 5   # detik

        # --- Despawn ---
        self.lifetime = 60  # detik
        self.despawn_timer = 0
        self.despawning = False
        self.despawn_frame = 0
        self.despawn_anim_speed = 0.09
        self.despawn_anim_timer = 0

        self.damage_active = False  # Flag for damage area

        self.fading_out = False     # Untuk status fade out
        self.fx_alpha = 255         # Untuk fade out setelah despawn

    def spawn_random(self, map_width, map_height):
        edge = random.choice(["left", "right", "top", "bottom"])
        padding = 200
        
        if edge == "left":
            x = padding
            y = random.randint(padding, map_height - padding)
        elif edge == "right":
            x = map_width - padding
            y = random.randint(padding, map_height - padding)
        elif edge == "top":
            x = random.randint(padding, map_width - padding)
            y = padding
        else:  # bottom
            x = random.randint(padding, map_width - padding)
            y = map_height - padding
            
        self.rect.center = (x, y)

    def update(self, dt, player_rect, enemies_group=None):
        if self.fading_out:
            # Fade out setelah despawn anim selesai
            self.fx_alpha = max(0, self.fx_alpha - int(255 * dt * 2))  # 0.5 detik fade
            if self.fx_alpha == 0:
                self.kill()
            return

        if self.despawning:
            self.despawn_anim_timer += dt
            if self.despawn_anim_timer >= self.despawn_anim_speed:
                self.despawn_anim_timer = 0
                self.despawn_frame += 1
                if self.despawn_frame >= len(self.spawn_frames):
                    # Mulai fade out setelah animasi despawn selesai
                    self.fading_out = True
                    self.image = self.spawn_frames[-1]
                else:
                    self.image = self.spawn_frames[self.despawn_frame]
            return

        # Lifetime countdown
        self.despawn_timer += dt
        if self.despawn_timer >= self.lifetime and not self.despawning:
            self.despawning = True
            self.despawn_frame = 0
            self.image = self.spawn_frames[0]
            return

        # Check if player is in interaction range (inside circle)
        if player_rect:
            dx = self.rect.centerx - player_rect.centerx
            dy = self.rect.centery - player_rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Update player in range status
            self.is_player_in_range = distance <= self.damage_circle_radius
            
            # Activate circle when player is nearby
            if self.is_player_in_range:
                self.damage_circle_active = True
            else:
                # If player moved away
                if self.state == "guard":
                    self.state = "idle"
                    self.state_timer = 0
                    self.frame_idx = 0
                self.damage_circle_active = False
        
        # Old checking code (can be simplified)
        if player_rect and self.rect.colliderect(player_rect.inflate(80, 80)):
            if self.state == "idle":
                self.state = "guard"
                self.state_timer = 0
                self.guard_idx = 0
                self.guard_completed = False
                self.damage_circle_active = True
    
        # State machine
        if self.state == "spawn":
            self.state_timer += dt
            if self.state_timer >= 0.1:
                self.state_timer = 0
                self.spawn_frame += 1
                if self.spawn_frame >= len(self.spawn_frames):
                    self.state = "idle"
                    self.frame_idx = 0
                    self.image = self.idle_frames[0]
                else:
                    self.image = self.spawn_frames[self.spawn_frame]
        elif self.state == "idle":
            self.state_timer += dt
            if self.state_timer >= 0.1:  # 100ms per frame
                self.state_timer = 0
                self.frame_idx = (self.frame_idx + 1) % len(self.idle_frames)
                self.image = self.idle_frames[self.frame_idx]
        elif self.state == "guard":
            self.state_timer += dt
            if self.state_timer >= 0.1:  # 100ms per frame
                self.state_timer = 0
                if not self.guard_completed:
                    self.guard_idx += 1
                    if self.guard_idx >= len(self.guard_frames):
                        self.guard_completed = True
                        self.guard_idx = len(self.guard_frames) - 1
                        self.damage_active = True
                
                self.image = self.guard_frames[self.guard_idx]

        # Always kill enemies in circle - even if shop mode is enabled
        # This combines protection functionality with shop functionality
        if (self.damage_circle_active or self.damage_active) and enemies_group is not None:
            circle_center = self.rect.center
            for enemy in enemies_group:
                # Skip enemies that are already dying
                if enemy.is_dying:
                    continue
                    
                # Calculate distance from enemy to devil
                dx = enemy.rect.centerx - circle_center[0]
                dy = enemy.rect.centery - circle_center[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # If enemy within circle radius
                if distance <= self.damage_circle_radius:
                    enemy.health = 0
                    enemy.is_dying = True
                    enemy.killed_by_devil = True  # This flag prevents XP drop
    
    # Split the drawing methods to control layering
    def draw_damage_circle(self, surface, camera_offset):
        """Draw only the damage circle layer - now repurposed as interaction circle"""
        if self.damage_circle_active or self.damage_active:
            # Create a transparent surface for the circle
            circle_surface = pygame.Surface((self.damage_circle_radius * 2, 
                                           self.damage_circle_radius * 2), 
                                           pygame.SRCALPHA)
            
            # Changed color to be friendlier - more golden/yellow for shop
            circle_color = (255, 215, 0, 60) if self.is_shop_enabled else self.damage_circle_color
            
            # Draw circle on the transparent surface
            pygame.draw.circle(circle_surface, 
                              circle_color, 
                              (self.damage_circle_radius, self.damage_circle_radius), 
                              self.damage_circle_radius)
            
            # Get position to place circle surface
            circle_pos = (self.rect.centerx - self.damage_circle_radius + camera_offset[0],
                         self.rect.centery - self.damage_circle_radius + camera_offset[1])
            
            # Apply fade effect if devil is fading out
            if self.fading_out:
                circle_surface.set_alpha(self.fx_alpha)
                
            # Draw circle to main surface
            surface.blit(circle_surface, circle_pos)
    
    def draw_shadow(self, surface, camera_offset):
        """Draw only the shadow layer"""
        shadow_img = self.shadow_img.copy()
        if self.fading_out:
            shadow_img.set_alpha(self.fx_alpha)
        shadow_rect = shadow_img.get_rect(center=(self.rect.centerx + camera_offset[0], 
                                                self.rect.bottom + camera_offset[1] - self.shadow_img.get_height()//2))
        surface.blit(shadow_img, shadow_rect)
    
    def draw_character(self, surface, camera_offset):
        """Draw only the devil character layer"""
        img = self.image.copy()
        if self.fading_out:
            img.set_alpha(self.fx_alpha)
        surface.blit(img, (self.rect.x + camera_offset[0], self.rect.y + camera_offset[1]))
    
    def draw(self, surface, camera_offset):
        """
        Main draw method that implements the layering:
        1. Circle (bottom layer)
        2. Shadow (middle layer)
        3. Character (top layer)
        """
        # Layer 3 (bottom) - Damage circle
        self.draw_damage_circle(surface, camera_offset)
        
        # Layer 2 (middle) - Shadow
        self.draw_shadow(surface, camera_offset)
        
        # Layer 1 (top) - Character
        self.draw_character(surface, camera_offset)
    
    def can_interact(self):
        return self.is_player_in_range and self.is_shop_enabled