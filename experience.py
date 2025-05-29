import pygame
import os
from settings import YELLOW  # Mengimpor warna kuning (YELLOW) dari file settings

# Kelas animasi Experience (XP) saat player mendapatkan XP dari musuh
class Experience(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        self.frames = []  # Menyimpan frame-frame animasi XP
        
        # Memuat 9 gambar animasi XP dari folder assets/xp
        for i in range(9):
            path = os.path.join('assets', 'xp', f'exp{i:03d}.png')  # Format: exp000.png hingga exp008.png
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (32, 32))  # Skala ukuran menjadi 32x32
            self.frames.append(image)
            
        self.frame_index = 0  # Indeks frame saat ini
        self.animation_timer = 0  # Timer untuk animasi
        self.animation_speed = 0.15  # Kecepatan animasi (semakin kecil, semakin cepat)
        self.animation_finished = False  # Status animasi selesai atau belum
        
        self.image = self.frames[0]  # Gambar awal
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)  # Menentukan posisi XP di layar
        
    def update(self):
        # Perbarui animasi hanya jika belum selesai
        if not self.animation_finished:
            self.animation_timer += 1  # Tambahkan waktu
            
            # Jika waktu cukup, lanjut ke frame berikutnya
            if self.animation_timer >= self.animation_speed * 60:
                self.animation_timer = 0
                
                if self.frame_index < len(self.frames) - 1:
                    self.frame_index += 1
                    self.image = self.frames[self.frame_index]
                    
                    # Tandai bahwa animasi sudah selesai di frame terakhir
                    if self.frame_index == len(self.frames) - 1:
                        self.animation_finished = True

# Kelas efek saat player naik level
class LevelUpEffect(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        
        self.frames = []  # Menyimpan frame-frame animasi efek naik level
        
        # Memuat 7 frame animasi dari folder assets/xp
        for i in range(7):
            path = os.path.join('assets', 'xp', f'lvlup{i}.png')
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, (96, 96))  # Ukuran efek diperbesar
            self.frames.append(image)
            
        self.frame_index = 0  # Frame awal
        self.animation_speed = 0.15  # Kecepatan transisi antar frame
        self.animation_timer = 0  # Timer untuk frame
        
        self.image = self.frames[self.frame_index]  # Gambar pertama animasi
        self.rect = self.image.get_rect()
        self.player = player  # Menyimpan referensi ke objek player
        self.finished = False  # Status apakah animasi sudah selesai
        
    def update(self, dt):
        self.rect.center = self.player.rect.center  # Posisikan efek di atas player
        
        self.animation_timer += dt  # Tambahkan delta time ke timer
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1  # Lanjut ke frame berikutnya
            
            if self.frame_index >= len(self.frames):
                self.finished = True  # Tandai selesai
                self.kill()  # Hapus sprite dari grup
            else:
                self.image = self.frames[self.frame_index]  # Tampilkan frame berikutnya

