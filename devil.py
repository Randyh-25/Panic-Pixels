import pygame
import os
import random

DEVIL_SIZE = (256, 256)
FX_SIZE = (DEVIL_SIZE[0] + 20, DEVIL_SIZE[1] + 20)

class Devil(pygame.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super().__init__()
        # Idle anim
        self.idle_frames = []
        for i in range(1, 9):
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

        # FX anim
        self.fx_frames = []
        for i in range(9):
            path = os.path.join("assets", "devil", "guard", "fx", f"fx{i}.png")
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, FX_SIZE)
            self.fx_frames.append(img)

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

        self.frame_idx = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.guard_idx = 0
        self.guard_timer = 0
        self.guard_speed = 0.08

        self.fx_idx = 0
        self.fx_timer = 0
        self.fx_speed = 0.08
        self.show_fx = False

        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.spawn_random(map_width, map_height)

        # --- Guard/Idle switching ---
        self.state = "idle"  # idle, guard, despawn
        self.state_timer = 0
        self.guard_duration = 1.2  # detik
        self.idle_duration = 5   # detik

        # --- Despawn ---
        self.lifetime = 60  # detik
        self.despawn_timer = 0
        self.despawning = False
        self.despawn_frame = 0
        self.despawn_anim_speed = 0.09
        self.despawn_anim_timer = 0

        # Tambah variabel untuk fade out
        self.fx_started = False  # Tambah flag FX sudah mulai
        self.fx_alpha = 255      # Untuk fade out setelah despawn
        self.fading_out = False  # Untuk status fade out

    def spawn_random(self, map_width, map_height):
        self.rect.center = (
            random.randint(100, map_width - 100),
            random.randint(100, map_height - 100)
        )

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
        else:
            if self.state == "guard":
                self.state = "idle"
                self.state_timer = 0
                self.frame_idx = 0
                self.show_fx = False

        # --- State machine for guard/idle switching ---
        self.state_timer += dt
        if self.state == "guard":
            self.guard_timer += dt
            if self.guard_timer >= self.guard_speed:
                self.guard_timer = 0
                if self.guard_idx < len(self.guard_frames) - 1:
                    self.guard_idx += 1
            self.image = self.guard_frames[self.guard_idx]
            if self.state_timer >= self.guard_duration:
                self.state = "idle"
                self.state_timer = 0
                self.frame_idx = 0
                # FX mulai setelah guard pertama selesai
                if not self.fx_started:
                    self.fx_started = True
                    self.fx_idx = 0
        elif self.state == "idle":
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_idx = (self.frame_idx + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.frame_idx]
            if self.state_timer >= self.idle_duration:
                self.state = "guard"
                self.state_timer = 0
                self.guard_idx = 0

        # FX anim (FX jalan terus jika sudah pernah aktif)
        if self.fx_started:
            self.fx_timer += dt
            if self.fx_timer >= self.fx_speed:
                self.fx_timer = 0
                self.fx_idx = (self.fx_idx + 1) % len(self.fx_frames)

        # FX kill musuh (FX area aktif terus jika sudah pernah aktif)
        if self.fx_started and enemies_group is not None:
            fx_rect = self.rect.copy()
            fx_rect.inflate_ip(40, 40)
            for enemy in enemies_group:
                if fx_rect.colliderect(enemy.rect) and not enemy.is_dying:
                    enemy.health = 0
                    enemy.is_dying = True
                    enemy.killed_by_devil = True

    def draw(self, surface, camera_offset):
        # Draw shadow (ikut fade out jika fading_out)
        shadow_img = self.shadow_img.copy()
        if self.fading_out:
            shadow_img.set_alpha(self.fx_alpha)
        shadow_rect = shadow_img.get_rect(center=(self.rect.centerx + camera_offset[0], self.rect.bottom + camera_offset[1] - self.shadow_img.get_height()//2))
        surface.blit(shadow_img, shadow_rect)
        # Draw devil (fade out jika fading_out)
        img = self.image.copy()
        if self.fading_out:
            img.set_alpha(self.fx_alpha)
        surface.blit(img, (self.rect.x + camera_offset[0], self.rect.y + camera_offset[1]))
        # Draw FX jika sudah pernah aktif, selalu di tengah devil
        if self.fx_started:
            fx_img = self.fx_frames[self.fx_idx].copy()
            if self.fading_out:
                fx_img.set_alpha(self.fx_alpha)
            fx_rect = fx_img.get_rect(center=self.rect.center)
            surface.blit(fx_img, (fx_rect.x + camera_offset[0], fx_rect.y + camera_offset[1]))