import pygame
import os
import random

DEVIL_SIZE = (256, 256)  # Misal player 48x48, devil 96x96
FX_SIZE = (DEVIL_SIZE[0] + 20, DEVIL_SIZE[1] + 20) # FX sedikit lebih besar

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

        self.frame_idx = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.guard_idx = 0
        self.guard_timer = 0
        self.guard_speed = 0.08
        self.is_guarding = False

        self.fx_idx = 0
        self.fx_timer = 0
        self.fx_speed = 0.08
        self.show_fx = False

        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.spawn_random(map_width, map_height)

    def spawn_random(self, map_width, map_height):
        self.rect.center = (
            random.randint(100, map_width - 100),
            random.randint(100, map_height - 100)
        )

    def update(self, dt, player_rect, enemies_group=None):
        # Cek proximity untuk trigger guard
        if self.rect.colliderect(player_rect.inflate(80, 80)):
            self.is_guarding = True
            self.show_fx = True

        # Idle/guard anim
        if self.is_guarding:
            self.guard_timer += dt
            if self.guard_timer >= self.guard_speed:
                self.guard_timer = 0
                self.guard_idx = (self.guard_idx + 1) % len(self.guard_frames)
            self.image = self.guard_frames[self.guard_idx]
        else:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_idx = (self.frame_idx + 1) % len(self.idle_frames)
            self.image = self.idle_frames[self.frame_idx]

        # FX anim
        if self.show_fx:
            self.fx_timer += dt
            if self.fx_timer >= self.fx_speed:
                self.fx_timer = 0
                self.fx_idx = (self.fx_idx + 1) % len(self.fx_frames)

        # FX kill musuh
        if self.show_fx and enemies_group is not None:
            fx_rect = self.rect.copy()
            fx_rect.inflate_ip(40, 40)
            for enemy in enemies_group:
                if fx_rect.colliderect(enemy.rect) and not enemy.is_dying:
                    enemy.health = 0
                    enemy.is_dying = True
                    enemy.killed_by_devil = True

    def draw(self, surface, camera_offset):
        # Draw devil
        surface.blit(self.image, (self.rect.x + camera_offset[0], self.rect.y + camera_offset[1]))
        # Draw FX jika aktif, selalu di tengah devil
        if self.show_fx:
            fx_img = self.fx_frames[self.fx_idx]
            fx_rect = fx_img.get_rect(center=self.rect.center)
            surface.blit(fx_img, (fx_rect.x + camera_offset[0], fx_rect.y + camera_offset[1]))