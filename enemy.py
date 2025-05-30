import pygame
import random
import math
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__()
        try:
            # load bayangan musush dari file gambar
            self.shadow_img = pygame.image.load("assets/shadow.png").convert_alpha()
            shadow_size = (100, 50) # ukuran bayangan yang diinginkan
            self.shadow_img = pygame.transform.scale(self.shadow_img, shadow_size)
            self.shadow_offset_y = -20 # offset vertikal bayangan terhadap musuh
        except pygame.error as e:
            print(f"Error loading shadow sprite: {e}")
            self.shadow_img = None # gunakan none jika gambar gagal dimuat

        # load efek suara ketika musuh terkena pukulan
        self.hit_sounds = []
        for i in range(1, 4): 
            try:
                sound_path = os.path.join("assets", "sound", "fly-eye", f"hit ({i}).ogg")
                hit_sound = pygame.mixer.Sound(sound_path)
                hit_sound.set_volume(0.2)  # suara diperkecil agar tidak mengganggu
                self.hit_sounds.append(hit_sound)
            except pygame.error as e:
                print(f"Error loading hit sound: {sound_path}")
                print(e)

        # load efek suara ketika musuh mati
        try:
            self.death_sound = pygame.mixer.Sound(os.path.join("assets", "sound", "fly-eye", "death.ogg"))
            self.death_sound.set_volume(0.2)  # volume juga dikecilkan
        except pygame.error as e:
            print(f"Error loading death sound")
            print(e)
            self.death_sound = None # none jika gagal dimuat

        # load sprite animasi berjalan musuh
        self.walk_frames = []
        for i in range(8):
            path = os.path.join("assets", "enemy", "fly-eye", "walk", f"fly{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (128, 128)) # skala gambar
                self.walk_frames.append(image) # menambahkan ke daftar frame
            except pygame.error as e:
                print(f"Error loading enemy sprite: {path}")
                print(e)
        
        self.hit_frames = [] # menyimpan frame animasi saat musuh terkena hit
        for i in range(4):
            path = os.path.join("assets", "enemy", "fly-eye", "hit", f"hit{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha() # memuat gambar dengan transparansi
                image = pygame.transform.scale(image, (128, 128))
                self.hit_frames.append(image) # menambahkan ke list animasi hit
            except pygame.error as e:
                print(f"Error loading hit sprite: {path}")
                print(e)
        
        self.death_frames = [] # menyimpan frame animasi kematian musuh
        for i in range(4):
            path = os.path.join("assets", "enemy", "fly-eye", "death", f"death{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (128, 128))
                self.death_frames.append(image)
            except pygame.error as e:
                print(f"Error loading death sprite: {path}")
                print(e)

        # Load attack frames
        self.attack_frames = []
        for i in range(8):
            path = os.path.join("assets", "enemy", "fly-eye", "attack", f"attack{i}.png")
            try:
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, (128, 128))
                self.attack_frames.append(image)
            except pygame.error as e:
                print(f"Error loading attack sprite: {path}")
                print(e)
        
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.animation_time = 0
        
        self.is_dying = False
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.2

        # attack properties
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 0.8
        self.attack_damage = 10
        self.attack_range = 70
        self.attack_cooldown = 0
        self.attack_cooldown_duration = 1.5
        self.damage_frame = 5
        self.has_dealt_damage = False
        
        self.image = self.walk_frames[0]
        self.rect = self.image.get_rect()
        self.spawn(player_pos)
        self.speed = random.uniform(1, 3)
        self.health = 30
        
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.separation_radius = 60
        
        self.facing_left = False

        self.fading_out = False
        self.fade_alpha = 255

    def spawn(self, player_pos):
        spawn_distance = 400 # jarak musuh muncul dari posisi pemain
        angle = random.uniform(0, 2 * math.pi) # menentukan arah acaj dalam lingkaran penuh
        spawn_x = player_pos[0] + math.cos(angle) * spawn_distance
        spawn_y = player_pos[1] + math.sin(angle) * spawn_distance
        
        self.rect.x = spawn_x
        self.rect.y = spawn_y
        self.pos = pygame.math.Vector2(self.rect.center) # memperbarui posisi vektor untuk gerakan

    def take_hit(self, damage):
        if self.is_dying:
            return # jika musuh sudah dalam proses kematian, abaikan damage selanjutnya
        
        self.health -= damage
        self.is_hit = True
        self.hit_timer = 0
        
        if self.health <= 0:
            self.is_dying = True
            self.current_frame = 0
            # play death sound
            if hasattr(self, 'death_sound') and self.death_sound: # jika suara kematian tersedia 
                self.death_sound.play() # mainkan suara kematian
        else:
            # mainkan suara hit acak jika musuh terkena tetapi belum mati
            if hasattr(self, 'hit_sounds') and self.hit_sounds:
                random.choice(self.hit_sounds).play()

    def start_hit_animation(self):
        # animasi saat musuh terkena hit
        self.is_hit = True
        self.hit_timer = 0 # reset durasi animasi hit
        self.current_frame = 0

    def start_attack_animation(self):
        # mulai animasi serangan
        self.is_attacking = True
        self.attack_timer = 0
        self.has_dealt_damage = False

    def start_death_animation(self):
        # mulai animasi kematian
        self.is_dying = True
        self.current_frame = 0
        self.animation_timer = 0

    def separate_from_enemies(self, enemies):
        # logika untuk menjaga jarak antara musuh agar tidak saling bertumpukan
        separation = pygame.math.Vector2()
        total = 0
        
        for enemy in enemies:
            if enemy != self:
                # menghitung vektor jarak antara musuh satu dan lainnya
                distance = pygame.math.Vector2(
                    self.rect.centerx - enemy.rect.centerx,
                    self.rect.centery - enemy.rect.centery
                )
                dist_length = distance.length()

                # jika musuh berada dalam radius pemisahan
                if dist_length < self.separation_radius:
                    if dist_length > 0:
                        separation += distance.normalize() / dist_length
                    else:
                        angle = random.uniform(0, 2 * math.pi)
                        separation += pygame.math.Vector2(
                            math.cos(angle),
                            math.sin(angle)
                        )
                    total += 1
        
        if total > 0:
            separation = separation / total
            if separation.length() > 0:
                separation = separation.normalize() * self.speed
                return separation
        
        return pygame.math.Vector2()

    def animate(self, dt):
        if self.is_dying:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                if self.current_frame < len(self.death_frames) - 1:
                    # lanjutkan ke frame animasi kematian berikutnya
                    self.current_frame += 1
                    self.image = self.death_frames[self.current_frame]
                    if self.facing_left:
                        # jika musuh menghadap sebelah kiri, flip gambarnya
                        self.image = pygame.transform.flip(self.image, True, False)
                elif self.current_frame >= len(self.death_frames) - 1:
                    self.kill()
            return None, 0
        
        elif self.is_attacking:
            # menambahkan waktu yang berlalu ke attack_timer
            self.attack_timer += dt
            frame_progress = self.attack_timer / self.attack_duration
            frame_index = min(int(frame_progress * len(self.attack_frames)), len(self.attack_frames) - 1)
            self.image = self.attack_frames[frame_index]
            
            if self.facing_left:
                self.image = pygame.transform.flip(self.image, True, False)
            
            # hitung frame saat ini untuk mengecek apakah saat memberikan damage
            current_frame = int(self.attack_timer / self.attack_duration * len(self.attack_frames))
            if current_frame == self.damage_frame and not self.has_dealt_damage:
                self.has_dealt_damage = True
                return True, self.attack_damage
                
            # jika animasi serangan selesai
            if self.attack_timer >= self.attack_duration:
                self.is_attacking = False
                self.attack_cooldown = self.attack_cooldown_duration
            
            return None, 0
        
        elif self.is_hit:
            # menambahkan waktu ke hit_timer
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                # animasi hit selesai
                self.is_hit = False
                self.current_frame = 0
            else:
                # menghitung frame animasi hit berdasarkan proses waktu
                frame_index = int((self.hit_timer / self.hit_duration) * len(self.hit_frames))
                frame_index = min(frame_index, len(self.hit_frames) - 1)
                self.image = self.hit_frames[frame_index]
                if self.facing_left:
                    self.image = pygame.transform.flip(self.image, True, False)
            return None, 0
        
        else:
            # animasi berjalan normal jika tidak menyerang, tidak terkena hit, dan tidak mati
            self.animation_time += dt
            if self.animation_time >= self.animation_speed:
                self.animation_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.walk_frames)
                self.image = self.walk_frames[self.current_frame]
                if self.facing_left:
                    self.image = pygame.transform.flip(self.image, True, False)
            return None, 0

    def update(self, player, enemies=None):
        if self.is_dying:
            # jalankan animasi kematian
            finished = self.animate(1/60)
            if finished and not self.fading_out:
                self.fading_out = True
            if self.fading_out:
                # kurangi alpha untuk efek fade-out
                self.fade_alpha -= int(255 * (1/60) * 2)  # 0.5 detik fade
                if self.fade_alpha <= 0:
                    self.kill()
            return None, 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1/60 # kurangi cooldown setiap frame

        # menghitung vektor ke pemain
        to_player = pygame.math.Vector2(
            player.rect.centerx - self.rect.centerx,
            player.rect.centery - self.rect.centery
        )
        
        distance_to_player = to_player.length()
        
        if to_player.x != 0:
            self.facing_left = to_player.x < 0
        
        # Jika dalam jarak serang dan cooldown selesai
        if distance_to_player <= self.attack_range and self.attack_cooldown <= 0 and not self.is_attacking and not self.is_hit and not player.is_dying:
            self.start_attack_animation()
        
        # Animasi, dan dapatkan sinyal damage
        should_deal_damage, damage_amount = self.animate(1/60)
        
        # Jika perlu memberikan damage
        if should_deal_damage:
            return player, damage_amount
        
        if not self.is_attacking and not self.is_hit:
            if to_player.length() > 0:
                to_player = to_player.normalize() * self.speed
            
            separation = pygame.math.Vector2()
            if enemies:
                separation = self.separate_from_enemies(enemies)
            
            final_movement = to_player + separation
            
            if final_movement.length() > self.speed:
                final_movement = final_movement.normalize() * self.speed
            
            self.pos += final_movement
            self.rect.center = self.pos
        
        return None, 0

    def draw(self, surface, camera_offset):
        # draw shadow first
        if self.shadow_img is not None:
            shadow = self.shadow_img.copy()
            if getattr(self, "fading_out", False):
                shadow.set_alpha(self.fade_alpha)
            shadow_rect = shadow.get_rect(center=(self.rect.centerx + camera_offset[0], self.rect.bottom + camera_offset[1] - self.shadow_img.get_height()//2 + self.shadow_offset_y))
            surface.blit(shadow, shadow_rect)
        # draw enemy
        img = self.image.copy()
        if getattr(self, "fading_out", False):
            img.set_alpha(self.fade_alpha)
        surface.blit(img, (self.rect.x + camera_offset[0], self.rect.y + camera_offset[1]))
