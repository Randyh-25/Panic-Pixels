import pygame
import math
import random
import os
from settings import WIDTH, HEIGHT, GREEN

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, projectile_type="rock"):
        super().__init__()
        
        self.projectile_type = projectile_type # jenis proyektil, default adalah "rock"
        
        # Load rock images
        self.rock_images = [] # menyimpan gambar animasi batu (rock)
        for i in range(3):
            path = os.path.join("assets", "projectile", "rock", f"rock{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha() # memuat gambar dengan transparansi
                # Scale to appropriate size
                image = pygame.transform.scale(image, (16, 16)) # mengubah ukuran gambar
                self.rock_images.append(image)
            except pygame.error as e:
                print(f"Error loading rock sprite: {path}") # menampilkan error jika gambar gagal dimuat
                print(e)
                # fallback ke surface sederhana jika gambar gagal dimuat
                fallback = pygame.Surface((10, 10)) # membuat surface kecil
                fallback.fill(GREEN) # mengisi dengan warna hijau sebagai indikator error
                self.rock_images.append(fallback) # menambahkan surface fallback ke list gambar
        
        # Load fireball images
        self.fireball_frames = []
        for i in range(1, 6):  # FB001.png to FB005.png
            path = os.path.join("assets", "projectile", "fireball", f"FB00{i}.png")
            try:
                original_image = pygame.image.load(path).convert_alpha()
                
                # Get original dimensions and maintain aspect ratio
                orig_width = original_image.get_width()
                orig_height = original_image.get_height()
                
                # Calculate new dimensions preserving aspect ratio
                # Use a base width of 32 pixels and scale height proportionally
                scale_factor = 32 / orig_width
                new_width = 32
                new_height = int(orig_height * scale_factor)
                
                # Scale the image with the correct aspect ratio
                image = pygame.transform.scale(original_image, (new_width, new_height))
                self.fireball_frames.append(image)
            except pygame.error as e:
                print(f"Error loading fireball sprite: {path}")
                print(e)
                # Fallback to a simple surface if image loading fails
                fallback = pygame.Surface((16, 16))
                fallback.fill((255, 0, 0))  # Red for fireball
                self.fireball_frames.append(fallback)
        
        self.fireball_frame_index = 0
        self.fireball_animation_speed = 0.15
        self.fireball_animation_timer = 0
        
        # select image based on projectile type
        if self.projectile_type == "fireball":
            self.original_image = self.fireball_frames[0] # menggunakan frame pertama untuk fireball
        else:
            # memilih salah satu gambar batu secara acak untuk variasi visual
            self.original_image = random.choice(self.rock_images)
            
        self.image = self.original_image.copy() # menyalin gambar asli untuk manipulasi
        self.rect = self.image.get_rect() # mendapatkan area gambar untuk keperluan posisi dan tabrakan
        self.rect.center = start_pos # set posisi awal proyektil
        self.start_x, self.start_y = start_pos # menyimpan koordinat awal
        
        self.speed = 7 # kecepatan gerak proyektil
        self.damage = 15 if self.projectile_type == "fireball" else 10  # Fireball does more damage
        self.max_distance = 800
        self.rotation = 0
        self.rotation_speed = random.uniform(5, 15) if self.projectile_type == "rock" else 0  # No rotation for fireball

        # menghitung arah gerak dari start_pos ke target_pos
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1) # menghitung jarak ; menghindari pembagian nol
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed
        
        # menghitung sudut arah proyektil untuk keperluan rotasi
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # menentukan arah rotasi proyektil batu ; searah atau berlawanan 
        self.rotation_dir = random.choice([-1, 1])
        
        # jika fireball, rotasikan sprite agar menghadap ke arah gerakan
        if self.projectile_type == "fireball":
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def reset(self, start_pos, target_pos, projectile_type="rock"):
        self.projectile_type = projectile_type
        self.rect.center = start_pos
        self.start_x, self.start_y = start_pos
        
        # memilih ulang gambar dan parameter berdasarkan tipe proyektil
        if self.projectile_type == "fireball":
            self.original_image = self.fireball_frames[0]
            self.damage = 15  # Fireball does more damage
            self.rotation_speed = 0  # No rotation for fireball
            self.fireball_frame_index = 0
            self.fireball_animation_timer = 0
        else:
            # Randomly select one of the rocks
            self.original_image = random.choice(self.rock_images) # memilih acak gambar batu
            self.damage = 10 # batu memberikan damage standar
            self.rotation_speed = random.uniform(5, 15) # batu bisa berputar dengan kecepatan acak
        
        self.image = self.original_image.copy() menyalin gambar untuk manipulasi
        
        target_x, target_y = target_pos
        dx = target_x - self.start_x
        dy = target_y - self.start_y
        dist = max(math.hypot(dx, dy), 0.1) # menghindari pembagian dengan nol
        self.dx = (dx / dist) * self.speed
        self.dy = (dy / dist) * self.speed
        
        # menghitung sudut arah gerakan
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # jika proyektil fireball, rotasikan gambar agar menghadap arah tembakan
        if self.projectile_type == "fireball":
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center) # set rect ulang setelah rotasi
            
        # Reset rotation direction
        self.rotation_dir = random.choice([-1, 1])
        self.rotation = 0

    def update(self, dt=1/60):
        # memperbaharui posisi proyektil berdasarkan arah
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        if self.projectile_type == "fireball":
            # memperbaharui animasi fireball berdasarkan waktu
            self.fireball_animation_timer += dt
            if self.fireball_animation_timer >= self.fireball_animation_speed:
                self.fireball_animation_timer = 0 # reset timer animasi
                self.fireball_frame_index = (self.fireball_frame_index + 1) % len(self.fireball_frames)
                self.original_image = self.fireball_frames[self.fireball_frame_index] # ambil frame animasi baru
                
                # rotasi gambar agar tetap menghadap arah tembakan
                self.image = pygame.transform.rotate(self.original_image, -self.angle)
                old_center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = old_center
        else:
            # untuk proyektil batu, lakukan rotasi terus-menerus
            self.rotation += self.rotation_speed * self.rotation_dir
            self.rotation %= 360  # Keep rotation angle between 0 and 360
            
            # Rotate the image
            self.image = pygame.transform.rotate(self.original_image, self.rotation)
            
            # Keep the rect centered at the same position after rotation
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
        
        # mengecek apakah proyektil telah menempuh jarak melebihi batas maksimum
        distance = math.hypot(self.rect.centerx - self.start_x, 
                            self.rect.centery - self.start_y)
        
        if distance > self.max_distance:
            self.kill() # menghapus proyektil dari grup sprite jika terlalu jauh
