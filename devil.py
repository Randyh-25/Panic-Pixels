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

        # Circle damage area
        self.damage_circle_radius = DAMAGE_CIRCLE_RADIUS
        self.damage_circle_color = (255, 0, 0, 80)  # Semi-transparent red
        self.damage_circle_active = False

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

        # Cek proximity untuk trigger guard
        if self.rect.colliderect(player_rect.inflate(80, 80)):
            if self.state == "idle":
                self.state = "guard"
                self.state_timer = 0
                self.guard_idx = 0
                self.guard_completed = False
                self.damage_circle_active = True
        else:
            if self.state == "guard":
                self.state = "idle"
                self.state_timer = 0
                self.frame_idx = 0
                self.damage_circle_active = False

        # --- State machine for guard/idle switching ---
        self.state_timer += dt
        if self.state == "guard":
            self.guard_timer += dt
            if self.guard_timer >= self.guard_speed:
                self.guard_timer = 0
                if self.guard_idx < len(self.guard_frames) - 1:
                    self.guard_idx += 1
                else:
                    # Keep last frame showing and mark animation as completed
                    self.guard_completed = True
            
            self.image = self.guard_frames[self.guard_idx]
            
            # Only transition to idle if both timer expired AND animation completed
            if self.state_timer >= self.guard_duration and self.guard_completed:
                self.state = "idle"
                self.state_timer = 0
                self.frame_idx = 0
                self.damage_active = True  # Activate damage after guard animation
        elif self.state == "idle":
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_idx = (self.frame_idx + 1) % len(self.idle_frames)
                # Make sure image is updated every frame
                self.image = self.idle_frames[self.frame_idx]
                
            if self.state_timer >= self.idle_duration:
                self.state = "guard"
                self.state_timer = 0
                self.guard_idx = 0
                self.guard_completed = False

        # Check for enemies in damage circle
        if (self.damage_circle_active or self.damage_active) and enemies_group is not None:
            circle_center = self.rect.center
            for enemy in enemies_group:
                # Calculate distance from enemy to devil
                dx = enemy.rect.centerx - circle_center[0]
                dy = enemy.rect.centery - circle_center[1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                # If enemy within circle radius and not already dying
                if distance <= self.damage_circle_radius and not enemy.is_dying:
                    enemy.health = 0
                    enemy.is_dying = True
                    enemy.killed_by_devil = True  # This flag prevents XP drop
    
    # Split the drawing methods to control layering
    def draw_damage_circle(self, surface, camera_offset):
        """Draw only the damage circle layer"""
        if self.damage_circle_active or self.damage_active:
            # Create a transparent surface for the circle
            circle_surface = pygame.Surface((self.damage_circle_radius * 2, 
                                           self.damage_circle_radius * 2), 
                                           pygame.SRCALPHA)
            
            # Draw circle on the transparent surface
            pygame.draw.circle(circle_surface, 
                              self.damage_circle_color, 
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