import pygame
import os
import random
import math

DEVIL_SIZE = (256, 256)  # Ukuran sprite devil
DAMAGE_CIRCLE_RADIUS = 180  # Radius lingkaran interaksi (awalnya damage)

class Devil(pygame.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super().__init__()

        # Animasi idle
        self.idle_frames = []
        for i in range(1, 8):
            # membuat path untuk setiap frame gambar animasi idle
            path = os.path.join("assets", "devil", "idle", f"idle ({i}).png")
            # membuat gambar dan menghapus latar belakang 
            img = pygame.image.load(path).convert_alpha()
            # mengubah ukuran gambar sesuai ukuran DEVIL_SIZE
            img = pygame.transform.scale(img, DEVIL_SIZE)
            # menambahkan gambar ke daftar frame
            self.idle_frames.append(img)

        # animasi guard (menjaga)
        self.guard_frames = []
        for i in range(1, 14):
            path = os.path.join("assets", "devil", "guard", f"guard ({i}).png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, DEVIL_SIZE)
            self.guard_frames.append(img)

        # Animasi spawn/despawn (muncul/menghilang)
        self.spawn_frames = []
        for i in range(1, 10):
            path = os.path.join("assets", "devil", "spawn", f"spawn ({i}).png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, DEVIL_SIZE)
            self.spawn_frames.append(img)

        # Gambar bayangan devil
        self.shadow_img = pygame.image.load(os.path.join("assets", "shadow.png")).convert_alpha()
        self.shadow_img = pygame.transform.scale(self.shadow_img, (DEVIL_SIZE[0], DEVIL_SIZE[1] // 3))

        # Lingkaran interaksi (dulunya area damage)
        self.damage_circle_radius = DAMAGE_CIRCLE_RADIUS
        self.damage_circle_color = (255, 0, 0, 80)  # Merah transparan
        self.damage_circle_active = False  # Default: tidak aktif

        # status interaksi
        self.is_player_in_range = False
        self.is_shop_enabled = True  # Devil sekarang menjadi penjaga toko

        # setup animasi
        self.frame_idx = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.guard_idx = 0
        self.guard_timer = 0
        self.guard_speed = 0.08
        self.guard_completed = False  # Flag animasi guard selesai

        # gambar awal dan posisi awal
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.spawn_random(map_width, map_height)

        # status animasi dan waktu
        self.state = "idle"  # idle, guard, spawn, despawn
        self.state_timer = 0
        self.guard_duration = 5
        self.idle_duration = 5

        # Timer dan flag untuk despawn
        self.lifetime = 60  # Devil hanya bertahan 60 detik
        self.despawn_timer = 0
        self.despawning = False
        self.despawn_frame = 0
        self.despawn_anim_speed = 0.09
        self.despawn_anim_timer = 0

        self.damage_active = False  # flag untuk fungsi damage

        self.fading_out = False  # Untuk fade-out saat menghilang
        self.fx_alpha = 255  # transparansi saat fade-out

    def spawn_random(self, map_width, map_height):
        """Memposisikan devil secara acak di tepi map"""
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
        else:
            x = random.randint(padding, map_width - padding)
            y = map_height - padding
            
        self.rect.center = (x, y)

    def update(self, dt, player_rect, enemies_group=None):
        """Update animasi dan interaksi devil"""
        if self.fading_out:
            # menghilang perlahan
            self.fx_alpha = max(0, self.fx_alpha - int(255 * dt * 2))
            if self.fx_alpha == 0:
                self.kill()
            return

        if self.despawning:
            # animasi menghilang
            self.despawn_anim_timer += dt
            if self.despawn_anim_timer >= self.despawn_anim_speed:
                self.despawn_anim_timer = 0
                self.despawn_frame += 1
                if self.despawn_frame >= len(self.spawn_frames):
                    self.fading_out = True
                    self.image = self.spawn_frames[-1]
                else:
                    self.image = self.spawn_frames[self.despawn_frame]
            return

        # timer hidup devil
        self.despawn_timer += dt
        if self.despawn_timer >= self.lifetime and not self.despawning:
            self.despawning = True
            self.despawn_frame = 0
            self.image = self.spawn_frames[0]
            return

        # Hitung jarak pemain dengan devil
        if player_rect:
            dx = self.rect.centerx - player_rect.centerx
            dy = self.rect.centery - player_rect.centery
            distance = math.sqrt(dx*dx + dy*dy)
            
            self.is_player_in_range = distance <= self.damage_circle_radius
            self.damage_circle_active = self.is_player_in_range

            if not self.is_player_in_range and self.state == "guard":
                self.state = "idle"
                self.state_timer = 0
                self.frame_idx = 0
                self.damage_circle_active = False

        # Jika pemain mendekat, ubah state jadi guard
        if player_rect and self.rect.colliderect(player_rect.inflate(80, 80)):
            if self.state == "idle":
                self.state = "guard"
                self.state_timer = 0
                self.guard_idx = 0
                self.guard_completed = False
                self.damage_circle_active = True

        # State machine animasi
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
            if self.state_timer >= 0.1:
                self.state_timer = 0
                self.frame_idx = (self.frame_idx + 1) % len(self.idle_frames)
                self.image = self.idle_frames[self.frame_idx]

        elif self.state == "guard":
            self.state_timer += dt
            if self.state_timer >= 0.1:
                self.state_timer = 0
                if not self.guard_completed:
                    self.guard_idx += 1
                    if self.guard_idx >= len(self.guard_frames):
                        self.guard_completed = True
                        self.guard_idx = len(self.guard_frames) - 1
                        self.damage_active = True
                self.image = self.guard_frames[self.guard_idx]

        # Deteksi musuh dalam area lingkaran
        if (self.damage_circle_active or self.damage_active) and enemies_group is not None:
            circle_center = self.rect.center
            for enemy in enemies_group:
                if enemy.is_dying:
                    continue
                dx = enemy.rect.centerx - circle_center[0]
                dy = enemy.rect.centery - circle_center[1]
                distance = math.sqrt(dx*dx + dy*dy)
                if distance <= self.damage_circle_radius:
                    enemy.health = 0
                    enemy.is_dying = True
                    enemy.killed_by_devil = True  # Hindari drop XP

    def draw_damage_circle(self, surface, camera_offset):
        """Gambar lingkaran interaksi (di layer bawah)"""
        if self.damage_circle_active or self.damage_active:
            circle_surface = pygame.Surface((self.damage_circle_radius * 2, 
                                           self.damage_circle_radius * 2), 
                                           pygame.SRCALPHA)

            # Warna emas untuk toko, merah jika tidak
            circle_color = (255, 215, 0, 60) if self.is_shop_enabled else self.damage_circle_color

            pygame.draw.circle(circle_surface, 
                              circle_color, 
                              (self.damage_circle_radius, self.damage_circle_radius), 
                              self.damage_circle_radius)

            circle_pos = (self.rect.centerx - self.damage_circle_radius + camera_offset[0],
                         self.rect.centery - self.damage_circle_radius + camera_offset[1])

            if self.fading_out:
                circle_surface.set_alpha(self.fx_alpha)

            surface.blit(circle_surface, circle_pos)

    def draw_shadow(self, surface, camera_offset):
        """Gambar bayangan devil (di layer tengah)"""
        shadow_img = self.shadow_img.copy()
        if self.fading_out:
            shadow_img.set_alpha(self.fx_alpha)
        shadow_rect = shadow_img.get_rect(center=(self.rect.centerx + camera_offset[0], 
                                                self.rect.bottom + camera_offset[1] - self.shadow_img.get_height()//2))
        surface.blit(shadow_img, shadow_rect)

    def draw_character(self, surface, camera_offset):
        """Gambar sprite devil (di layer atas)"""
        img = self.image.copy()
        if self.fading_out:
            img.set_alpha(self.fx_alpha)
        surface.blit(img, (self.rect.x + camera_offset[0], self.rect.y + camera_offset[1]))

    def draw(self, surface, camera_offset):
        """Gambar keseluruhan dengan urutan: circle → shadow → karakter"""
        self.draw_damage_circle(surface, camera_offset)
        self.draw_shadow(surface, camera_offset)
        self.draw_character(surface, camera_offset)

    def can_interact(self):
        """Cek apakah player bisa berinteraksi dengan devil"""
        return self.is_player_in_range and self.is_shop_enabled
