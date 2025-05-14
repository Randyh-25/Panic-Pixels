import pygame
import os
import random

class RockHitEffect(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.frames = []
        
        # Load gambar collapse dari c0.png - c2.png
        for i in range(3):
            try:
                path = os.path.join("assets", "enemy", "collapse", f"c{i}.png")
                image = pygame.image.load(path).convert_alpha()
                # Scale gambar sesuai kebutuhan
                image = pygame.transform.scale(image, (32, 32))
                self.frames.append(image)
            except pygame.error as e:
                print(f"Error loading collapse sprite: {path}")
                print(e)
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=position)
        
        self.frame_index = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        # Tambahkan sedikit offset acak untuk efek lebih natural
        self.rect.x += random.randint(-5, 5)
        self.rect.y += random.randint(-5, 5)
    
    def update(self, dt):
        self.animation_timer += dt
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1
            
            if self.frame_index >= len(self.frames):
                self.kill()  # Hapus efek setelah animasi selesai
            else:
                self.image = self.frames[self.frame_index]