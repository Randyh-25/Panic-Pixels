import pygame
import random
import math
import os

class BiEnemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__() # inisialisasi kelas induk sprite
        # Load shadow image
        try:
            self.shadow_img = pygame.image.load(os.path.join("assets", "shadow.png")).convert_alpha()
            shadow_size = (100, 50) # menentukan ukuran shadow
            self.shadow_img = pygame.transform.scale(self.shadow_img, shadow_size)
            self.shadow_offset_y = -20 # offset vertikal shadow dari posisi sprite
        except pygame.error as e:
            print(f"Error loading shadow sprite: {e}")
            self.shadow_img = None # set shadow image menjadi gagal jika load gagal

        # Load sound effects for bi
        self.hit_sounds = []
        for i in range(1, 4):
            try:
                sound_path = os.path.join("assets", "sound", "fly-eye", f"hit ({i}).ogg")  # Fixed the f-string
                hit_sound = pygame.mixer.Sound(sound_path)
                hit_sound.set_volume(0.2)  # Reduced volume so it's not distracting
                self.hit_sounds.append(hit_sound)
            except pygame.error as e:
                print(f"Error loading hit sound: {sound_path}")
                print(e)

        try:
            self.death_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "fly-eye", "death.ogg"))
            self.death_sound.set_volume(0.2)  # Reduced volume so it's not distracting
        except pygame.error as e:
            print(f"Error loading death sound")
            print(e)
            self.death_sound = None

        # Load idle frames
        self.idle_frames = []
        for i in range(4):
            path = os.path.join("assets", "enemy", "bi", "idle", f"idle00{i}.png") # membuat path file gambar idle
            try:
                image = pygame.image.load(path).convert_alpha() # load gambar dengan transparansi
                image = pygame.transform.scale(image, (32, 32)) # mengubah ukuran gambar
                self.idle_frames.append(image) # menambahkan gambar ke list frame idle
            except pygame.error as e:
                print(f"Error loading bi idle sprite: {path}") # mencetak path jika gagal load
                print(e)
        
        # Load hit frames
        self.hit_frames = []
        for i in range(4):
            path = os.path.join("assets", "enemy", "bi", "hit", f"hit00{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (32, 32))
                self.hit_frames.append(image)
            except pygame.error as e:
                print(f"Error loading bi hit sprite: {path}")
                print(e)

        # Load shoot frames
        self.shoot_frames = []
        for i in range(12):
            path = os.path.join("assets", "enemy", "bi", "shoot", f"shoot ({i}).png")
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (32, 32))
                self.shoot_frames.append(image)
            except pygame.error as e:
                print(f"Error loading bi shoot sprite: {path}")
                print(e)

        # Load death frames
        self.death_frames = []
        for i in range(4):
            path = os.path.join("assets", "enemy", "bi", "death", f"death ({i}).png")
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (32, 32))
                self.death_frames.append(image)
            except pygame.error as e:
                print(f"Error loading bi death sprite: {path}")
                print(e)

        # Load sting projectile
        try:
            self.sting_image = pygame.image.load(os.path.join("assets", "enemy", "bi", "sting.png")).convert_alpha()
            self.sting_image = pygame.transform.scale(self.sting_image, (32, 32))
        except pygame.error as e:
            print(f"Error loading sting projectile: {e}")
            self.sting_image = None
                
        # Initial setup
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.animation_time = 0
        
        self.is_dying = False
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.2
        
        # Direction for mirroring
        self.facing_right = True  # Default facing right

        # Shoot properties
        self.is_shooting = False
        self.shoot_timer = 0
        self.shoot_duration = 1.2
        self.shoot_damage = 8
        self.shoot_cooldown = 3.0  # Time between shots
        self.current_shoot_cooldown = random.uniform(1.0, 2.0)  # Initial random cooldown
        self.has_shot = False
        self.shoot_range = 500  # Maximum shooting range

        # General properties
        self.speed = 1.2  # Slower than regular enemies
        self.health = 30
        self.attack_damage = 10
        self.knockback_resistance = 0.8  # Higher resistance to knockback
        self.preferred_distance = 350  # Preferred distance from player (for ranged attacks)
        
        # Set up the sprite
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.spawn(player_pos)
        self.pos = pygame.math.Vector2(self.rect.center)

    def spawn(self, player_pos):
        spawn_distance = 400
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player_pos[0] + math.cos(angle) * spawn_distance
        spawn_y = player_pos[1] + math.sin(angle) * spawn_distance
        
        self.rect.x = spawn_x
        self.rect.y = spawn_y
        self.pos = pygame.math.Vector2(self.rect.center)

    def take_hit(self, damage):
        if self.is_dying:
            return
        
        self.health -= damage
        self.is_hit = True
        self.hit_timer = 0
        
        if self.health <= 0: # mencetak apakah health musuh sudah habis
            self.is_dying = True # menandai musuh yang sedang dalam kondisi mati
            self.current_frame = 0
            # Play death sound
            if hasattr(self, 'death_sound') and self.death_sound:  
                self.death_sound.play() # memainkan suara kematian
        else:
            # Play random hit sound when damaged but not dying
            if hasattr(self, 'hit_sounds') and self.hit_sounds:
                random.choice(self.hit_sounds).play() # pilih dan mainkan suara hit secara acak

    def start_hit_animation(self):
        self.is_hit = True
        self.hit_timer = 0
        self.current_frame = 0

    def start_shoot_animation(self):
        self.is_shooting = True
        self.shoot_timer = 0
        self.has_shot = False
        self.current_frame = 0

    def separate_from_enemies(self, enemies):
        for other in enemies:
            if other is not self and not other.is_dying:
                dx = self.rect.centerx - other.rect.centerx
                dy = self.rect.centery - other.rect.centery
                distance = math.hypot(dx, dy)
                if distance < 80:  # If too close to another enemy
                    if distance > 0:
                        # Move away slightly
                        self.pos.x += dx * 0.1
                        self.pos.y += dy * 0.1

    # Helper function to flip frames based on direction
    def get_frame_for_direction(self, frame):
        if self.facing_right:
            return frame
        else:
            return pygame.transform.flip(frame, True, False)

    def animate(self, dt):
        # Death animation
        if self.is_dying:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame += 1
                if self.current_frame >= len(self.death_frames):
                    self.kill()  # Remove sprite when animation is done
                else:
                    frame = self.death_frames[self.current_frame]
                    self.image = self.get_frame_for_direction(frame)
            return
        
        # Hit animation (when damaged)
        if self.is_hit:
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.current_frame = 0
            else:
                frame = min(int(self.hit_timer / self.hit_duration * len(self.hit_frames)), len(self.hit_frames) - 1)
                self.image = self.get_frame_for_direction(self.hit_frames[frame])
            return
        
        # Shooting animation
        if self.is_shooting:
            self.shoot_timer += dt
            if self.shoot_timer >= self.shoot_duration:
                self.is_shooting = False
                self.current_frame = 0
                self.has_shot = False
            else:
                frame = min(int(self.shoot_timer / self.shoot_duration * len(self.shoot_frames)), len(self.shoot_frames) - 1)
                self.image = self.get_frame_for_direction(self.shoot_frames[frame])
                # Trigger projectile creation at specific frame (around 1/3 through animation)
                if frame == 6 and not self.has_shot:
                    self.has_shot = True
                    return True  # Signal to create projectile
            return False
        
        # Idle animation
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
            self.image = self.get_frame_for_direction(self.idle_frames[self.current_frame])
        return False

    def update(self, player, enemies=None):
        if self.is_dying:
            self.animate(0.016)  # Use fixed dt for dying animation
            return None, 0
            
        # Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)
        
        # Update facing direction based on player position
        if dx > 0:
            self.facing_right = False  # Player is to the right, face right
        else:
            self.facing_right = True   # Player is to the left, face left
        
        # Update shooting cooldown
        if self.current_shoot_cooldown > 0:
            self.current_shoot_cooldown -= 0.016
        
        # If player is in range and cooldown is ready, start shooting
        if distance <= self.shoot_range and not self.is_shooting and self.current_shoot_cooldown <= 0:
            self.start_shoot_animation()
        
        # Move towards or away from player depending on preferred distance
        if not self.is_shooting and not self.is_hit:
            if distance > self.preferred_distance + 50:
                # Move towards player if too far
                angle = math.atan2(dy, dx)
                self.pos.x += math.cos(angle) * self.speed
                self.pos.y += math.sin(angle) * self.speed
            elif distance < self.preferred_distance - 50:
                # Move away from player if too close
                angle = math.atan2(dy, dx)
                self.pos.x -= math.cos(angle) * self.speed
                self.pos.y -= math.sin(angle) * self.speed
        
        # Separate from other enemies
        if enemies:
            self.separate_from_enemies(enemies)
            
        # Update position
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Update animation and check if we need to shoot
        should_shoot = self.animate(0.016)
        
        # If animation says we should create a projectile
        if should_shoot:
            self.current_shoot_cooldown = self.shoot_cooldown  # Reset cooldown
            # Return player as target with damage value
            return player, self.shoot_damage
            
        return None, 0

    def draw(self, surface, camera_offset):
        if self.shadow_img is not None:
            shadow = self.shadow_img.copy()
            if getattr(self, "fading_out", False):
                shadow.set_alpha(self.fade_alpha)
            shadow_rect = shadow.get_rect(center=(self.rect.centerx + camera_offset[0], self.rect.bottom + camera_offset[1] - self.shadow_img.get_height()//2 + self.shadow_offset_y))
            surface.blit(shadow, shadow_rect)

        # Check if we're dying or dead
        if self.is_dying:
            # Draw shadow first (even when dying)
            self.draw_shadow(surface, camera_offset)
            
            # Then draw the enemy
            x = self.rect.x + camera_offset[0]
            y = self.rect.y + camera_offset[1]
            surface.blit(self.image, (x, y))
            return
        
        # Then draw the enemy
        x = self.rect.x + camera_offset[0]
        y = self.rect.y + camera_offset[1]
        surface.blit(self.image, (x, y))

    def draw_shadow(self, surface, camera_offset):
        if self.shadow_img:
            shadow_x = self.rect.centerx - self.shadow_img.get_width() // 2 + camera_offset[0]
            shadow_y = self.rect.bottom - self.shadow_img.get_height() // 2 + self.shadow_offset_y + camera_offset[1]
            surface.blit(self.shadow_img, (shadow_x, shadow_y))
