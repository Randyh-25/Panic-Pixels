import pygame
import os
import random

class RockHitEffect(pygame.sprite.Sprite):
    def __init__(self, position): # konstruktor dengan posisi sebagai parameter
        super().__init__() # inisialisasi kelas induk
        self.frames = [] # menyimpan frame animasi
        
        for i in range(3):
            try:
                path = os.path.join("assets", "enemy", "collapse", f"c{i}.png") # path ke gambar frame 
                image = pygame.image.load(path).convert_alpha()
                # Scale gambar sesuai kebutuhan
                image = pygame.transform.scale(image, (32, 32)) # menskalakan gambar 
                self.frames.append(image) # menambahkan gambar ke list frame
            except pygame.error as e:
                print(f"Error loading collapse sprite: {path}")
                print(e)
        
        self.image = self.frames[0] # frame pertama 
        self.rect = self.image.get_rect(center=position)
        
        self.frame_index = 0 
        self.animation_speed = 0.2 # kecepatan animasi
        self.animation_timer = 0 # timer untuk mengatur pergantian frame
        
        # Tambahkan sedikit offset acak untuk efek lebih natural
        self.rect.x += random.randint(-5, 5)
        self.rect.y += random.randint(-5, 5)
    
    def update(self, dt):
        self.animation_timer += dt # menambahkan waktu delta ke timer animasi
        
        if self.animation_timer >= self.animation_speed: # jika timer melebihi kecepatan animasi
            self.animation_timer = 0 # reset timer
            self.frame_index += 1 # memindahkan ke frame animasi berikutnya
            
            if self.frame_index >= len(self.frames):
                self.kill()  # hapus efek setelah animasi selesai
            else:
                self.image = self.frames[self.frame_index]
