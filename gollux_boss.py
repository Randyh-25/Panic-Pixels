import pygame
import math
import os
import random
from settings import *

class Gollux(pygame.sprite.Sprite):
    def __init__(self, map_width, map_height, player_pos=None):
        super().__init__()
        
        # load dan siapkan sprite frames
        self.load_animations()
        
        # properti dasar
        self.health = 1000
        self.max_health = 1000
        self.speed = 0.8  # mengubah dari 2 menjadi 0.8 untuk gerakan lebih lambat
        self.attack_damage = 25
        self.attack_cooldown = 0
        self.attack_range = 150
        self.is_dying = False
        self.is_defeated = False
        
        # flinch system - tracking hits
        self.hit_counter = 0
        self.hits_to_flinch = 10  # butuh 10 hit untuk membuat gllux goyah
        self.is_flinching = False  # status flinch
        
        # posisi dan pergerakan
        self.pos = pygame.math.Vector2(0, 0)
        self.spawn_near_player(map_width, map_height, player_pos)
        self.target_pos = None
        self.facing_left = False
        
        # properti animasi
        self.current_animation = "idle"  # idle, walk, attack_a, attack_b, hit, death
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 0.25  # Animasi lebih lambat (dari 0.15 ke 0.25)
        
        # properti serangan
        self.attack_type = "a"  # Tipe serangan default
        self.attack_duration = 1.5  # Serangan lebih lambat (dari 1.5 ke 2.0)
        self.attack_timer = 0
        self.damage_frame_a = 10  # frame saat damage diberikan dalam serangan A
        self.damage_frame_b = 11  # frame saat damage diberikan dalam serangan B
        self.has_dealt_damage = False
        
        # properti saat terkena hit
        self.is_hit = False
        self.hit_timer = 0
        self.hit_duration = 0.4  # animasi hit lebih lambat (dari 0.4 ke 0.6)
        
        # properti shadow
        self.shadow = self.create_shadow()
        
        # sound timing propertis
        self.step_delay = 1200  # Perlambat suara langkah menjadi 1.5 detik
        self.last_step_time = 0
        
        # reference to sound manager
        # we'll set this when updating from the main game
        self.sound_manager = None
    
    def create_shadow(self):
        """Buat bayangan elips di bawah boss"""
        # dapatkan lebar sprite untuk ukuran bayangan
        if self.animations["idle"]:
            base_width = self.animations["idle"][0].get_width()
            shadow_width = int(base_width * 0.8)
            shadow_height = int(shadow_width * 0.3)
            
            # membuat surface bayangan dengan alpha
            shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
            
            # gambar elips bayangan dengan alpha gradient
            shadow_color = (0, 0, 0, 120)  # Hitam semi-transparan
            pygame.draw.ellipse(shadow, shadow_color, (0, 0, shadow_width, shadow_height))
            
            return shadow
        else:
            # fallback jika idle frames belum dimuat
            shadow = pygame.Surface((100, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 120), (0, 0, 100, 30))
            return shadow
        
    def load_animations(self):
        """Load dan pisahkan sprite sheets menjadi frame animasi"""
        # inisialisasi dictionary untuk semua animasi
        self.animations = {
            "idle": [],
            "walk": [],
            "attack_a": [],
            "attack_b": [],
            "hit": [],
            "death": []
        }
        
        # function untuk loading dan scaling sprite
        def load_sprite_sequence(folder, prefix, start_idx, end_idx, scale=2.0):
            frames = []
            for i in range(start_idx, end_idx + 1):
                try:
                    filepath = os.path.join("assets", "enemy", "boss-gollux", folder, f"{prefix}{i}.png")
                    image = pygame.image.load(filepath).convert_alpha()
                    
                    # scale gambar ke ukuran yang diinginkan
                    orig_width = image.get_width()
                    orig_height = image.get_height()
                    image = pygame.transform.scale(image, 
                                                 (int(orig_width * scale), int(orig_height * scale)))
                    frames.append(image)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}")
            return frames
        
        try:
            # load animasi idle (idle0.png - idle4.png)
            self.animations["idle"] = load_sprite_sequence("idle", "idle", 0, 4)
            
            # load animasi walk (walk0.png - walk7.png)
            self.animations["walk"] = load_sprite_sequence("walk", "walk", 0, 7)
            
            # load animasi hit (hit0.png - hit3.png)
            self.animations["hit"] = load_sprite_sequence("hit", "hit", 0, 3)
            
            # load animasi attack A (attacka0.png - attacka16.png) 
            self.animations["attack_a"] = load_sprite_sequence("attackA", "attacka", 0, 16)
            
            # load animasi attack B (attackb0.png - attackb18.png)
            self.animations["attack_b"] = load_sprite_sequence("attackB", "attackb", 0, 18)
            
            # load animasi death (death10.png - death20.png)
            self.animations["death"] = load_sprite_sequence("death", "death", 10, 20)
            
        except Exception as e:
            print(f"Error loading boss animations: {e}")
            
            # Fallback dengan surface kosong jika terjadi error
            dummy = pygame.Surface((200, 200), pygame.SRCALPHA)
            dummy.fill((255, 0, 255))  # Warna pink sebagai indikator error
            
            for key in self.animations:
                self.animations[key] = [dummy.copy() for _ in range(5)]
        
        # seat gambar awal dan react
        self.image = self.animations["idle"][0]
        self.rect = self.image.get_rect()
        
    def spawn_near_player(self, map_width, map_height, player_pos=None):
        """Posisikan Gollux dekat dengan player tapi sedikit di luar layar"""
        if player_pos is None:
            # fallback ke posisi acak di tepi jika tidak ada player_pos
            self.spawn_at_random_edge(map_width, map_height)
            return
            
        # jarak dari player untuk spawn (diluar layar)
        spawn_distance = 800
        
        # pilih sudut acak untuk memposisikan boss
        angle = random.uniform(0, 2 * math.pi)
        spawn_x = player_pos[0] + math.cos(angle) * spawn_distance
        spawn_y = player_pos[1] + math.sin(angle) * spawn_distance
        
        # pastikan boss berada dalam batas peta
        spawn_x = max(100, min(map_width - 100, spawn_x))
        spawn_y = max(100, min(map_height - 100, spawn_y))
            
        self.rect.center = (spawn_x, spawn_y)
        self.pos = pygame.math.Vector2(spawn_x, spawn_y)
        
    def spawn_at_random_edge(self, map_width, map_height):
        """Metode fallback untuk memposisikan Gollux di lokasi tepi peta secara acak"""
        edge = random.choice(["left", "right", "top", "bottom"])
        padding = 300 # jarak dari tepi peta
        
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
        self.pos = pygame.math.Vector2(x, y)
        
    def play_footstep(self):
        """Play footstep sound if enough time has passed and add slight screen shake"""
        current_time = pygame.time.get_ticks()
        # periksa apakah sudah lewat 1.5 detik sejak langkah terakhir
        if self.sound_manager and current_time - self.last_step_time >= self.step_delay:
            self.sound_manager.play_gollux_walk()
            self.last_step_time = current_time
            
            # tambahkan informasi untuk screen shake ringan
            return True  # Signal untuk screen shake
        return False

    def play_attack_sound(self):
        """Play attack sound"""
        if self.sound_manager:
            self.sound_manager.play_gollux_attack()
            
    def play_death_sound(self):
        """Play death sound"""
        if self.sound_manager:
            self.sound_manager.play_gollux_death()
        
    def update(self, dt, player, enemies=None):
        """Update boss position, animation and behavior"""
        if self.is_defeated:
            # Process death animation
            if self.current_animation != "death":
                self.current_animation = "death"
                self.frame_index = 0
                self.animation_timer = 0
                self.play_death_sound() # play death sound only once
            
            self.animate(dt)
            # jika animasi kematian selesai, hapus sprite
            if self.current_animation == "death" and self.frame_index >= len(self.animations["death"]) - 1:
                self.kill()
            
            return None, 0
            
        # handle cooldown serangan
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # jika terkena hit dan sedang dalam animasi flinch, proses animasi hit lebih dulu
        if self.is_hit:
            self.hit_timer += dt
            if self.hit_timer >= self.hit_duration:
                self.is_hit = False
                self.current_animation = "idle"
                self.frame_index = 0
            
            self.animate(dt)
            return None, 0
            
        # jika sedang menyerang, lanjutkan animasi serangan
        if self.current_animation in ["attack_a", "attack_b"]:
            self.attack_timer += dt
            
            total_frames = len(self.animations[self.current_animation])
            # calculate the exact frame based on timer
            exact_frame = self.attack_timer / self.attack_duration * total_frames
            target_frame = int(exact_frame)
            
            # update frame index if needed
            if target_frame != self.frame_index and target_frame < total_frames:
                self.frame_index = target_frame
                # get the correct frame
                self.update_image()
            
            # jika selesai menyerang
            if self.attack_timer >= self.attack_duration:
                self.current_animation = "idle"
                self.frame_index = 0
                self.attack_timer = 0
                self.has_dealt_damage = False
                self.attack_cooldown = 2.0  # 2 detik antara serangan
                self.update_image()
            else:
                # cek jika perlu memberikan damage pada frame tertentu
                damage_frame = self.damage_frame_a if self.current_animation == "attack_a" else self.damage_frame_b
                
                # jika kita di frame damage dan belum memberikan damage
                if target_frame == damage_frame and not self.has_dealt_damage:
                    self.play_attack_sound()  # play attack sound when dealing damage
                    self.has_dealt_damage = True
                    return player, self.attack_damage
                    
            return None, 0
                
        # target player jika masih hidup
        if player and player.health > 0:
            to_player = pygame.math.Vector2(
                player.rect.centerx - self.rect.centerx,
                player.rect.centery - self.rect.centery
            )
            
            distance_to_player = to_player.length()
            
            # menentukan arah menghadap berdasarkan posisi player
            if to_player.x != 0:
                self.facing_left = to_player.x < 0
                
            # pergerakan boss - mendekati player jika tidak dalam jarak serangan
            if distance_to_player > self.attack_range:
                was_walking = self.current_animation == "walk"
                
                # hanya ubah ke animasi walk jika belum berjalan
                if self.current_animation != "walk":
                    self.current_animation = "walk"
                    self.frame_index = 0
                
                # play walk sound only if already in walk animation
                if was_walking:
                    trigger_shake = self.play_footstep()
                    if trigger_shake and hasattr(player, 'camera'):
                        # berikan screen shake ringan - hanya jika player cukup dekat
                        if distance_to_player < 400:
                            shake_intensity = max(0.5, 3.0 - (distance_to_player / 400))
                            player.camera.add_trauma(shake_intensity * 0.05)  # Efek trauma kecil
            
                # normalisasi dan kalikan dengan kecepatan
                if to_player.length() > 0:
                    # menambahkan akselerasi bertahap untuk gerakan berat
                    target_velocity = to_player.normalize() * self.speed
                    
                    # lakukan pergerakan dengan lebih halus
                    movement_x = target_velocity.x
                    movement_y = target_velocity.y
                    
                    # tambahkan kesan berat
                    if was_walking:
                        # hanya berikan akselerasi penuh setelah beberapa frame animasi
                        if self.frame_index > 2: # setelah kaki terangkat dalam animasi
                            self.pos.x += movement_x
                            self.pos.y += movement_y
                    else:
                        # gerakan lebih lambat saat baru berjalan
                        self.pos.x += movement_x * 0.5
                        self.pos.y += movement_y * 0.5
            
                self.rect.center = (int(self.pos.x), int(self.pos.y))
            else:
                # dalam jarak serangan - mulai serangan jika colldown selesai
                if self.attack_cooldown <= 0:
                    # acak pilih serangan A atau B
                    self.attack_type = random.choice(["a", "b"])
                    self.current_animation = f"attack_{self.attack_type}"
                    self.frame_index = 0
                    self.attack_timer = 0
                    self.has_dealt_damage = False
                elif self.current_animation != "idle":
                    # tidak menyerang, hanya idle
                    self.current_animation = "idle"
                    self.frame_index = 0
        
        # update animasi
        self.animate(dt)
        
        return None, 0
        
    def animate(self, dt):
        """Update frame animasi"""
        # skip animasi khusus seperti attack dan death (ditangani di update)
        if self.current_animation in ["attack_a", "attack_b", "death"]:
            return
        
        # update timer animasi
        self.animation_timer += dt
        
        # update frame ketika timer melebihi kecepatan animasi
        animation_frames = self.animations[self.current_animation]
        if not animation_frames:
            return
            
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index = (self.frame_index + 1) % len(animation_frames)
            self.update_image()
    
    def update_image(self):
        """Update sprite image berdasarkan frame index dan arah hadap saat ini"""
        # dapatkan frame yang benar
        frames = self.animations[self.current_animation]
        if not frames or self.frame_index >= len(frames):
            return
            
        current_frame = frames[self.frame_index]
        
        # flip jika gambar menghadap kiri
        if self.facing_left:
            self.image = pygame.transform.flip(current_frame, True, False)
        else:
            self.image = current_frame
                
    def take_hit(self, damage):
        """Terima damage dari serangan player"""
        # selalu teriuma damage
        self.health -= damage
        
        # menambahkan hit counter dan periksa apakah sudah mencapau batas flinch
        self.hit_counter += 1
        
        # debug info
        print(f"Boss hit! Health: {self.health}/{self.max_health}, Hit counter: {self.hit_counter}/{self.hits_to_flinch}")
        
        # periksa apakah sudah mati
        if self.health <= 0:
            self.health = 0
            self.is_hit = False
            self.hit_counter = 0 # reset counter
            self.is_defeated = True
            self.current_animation = "death"
            self.frame_index = 0
            # Death sound is played in update method
            return True  # boss dikalahkan
        
        # hanya menampilkan animasi hit jika hit counter mencapai batas dan belum dikalahkan
        if self.hit_counter >= self.hits_to_flinch and not self.is_defeated:
            self.is_hit = True
            self.hit_timer = 0
            self.current_animation = "hit"
            self.frame_index = 0
            self.hit_counter = 0 # reset counter setelah menampilkan flinch
            
            # mainkan suara hit jika ada
            if hasattr(self, 'sound_manager') and self.sound_manager:
                # bisa menambahkan suara hit khusus di sound manager
                if hasattr(self.sound_manager, 'play_gollux_hurt'):
                    self.sound_manager.play_gollux_hurt()
    
        return False
        
    def draw_shadow(self, surface, camera_offset):
        """Gambar bayangan di bawah boss"""
        # posisikan bayangan di bawah sprite boss
        shadow_x = self.rect.centerx - self.shadow.get_width() // 2 + camera_offset[0]
        shadow_y = self.rect.bottom - 10 + camera_offset[1]
        
        # gambar bayangan
        surface.blit(self.shadow, (shadow_x, shadow_y))
        
    def draw(self, surface, camera_offset):
        """Gambar boss dengan health bar dan bayangan"""
        # gambar bayangan terlebih dahuly (dibawah karakter)
        self.draw_shadow(surface, camera_offset)
        
        # gambar sprite tanpa efek merah
        surface.blit(self.image, (self.rect.x + camera_offset[0], self.rect.y + camera_offset[1]))
        
        # jika boss belum mati, tampilkan health bar
        if not self.is_defeated:
            # gambar health bar diatas boss
            health_width = 200
            health_height = 20
            health_x = self.rect.centerx - health_width // 2 + camera_offset[0]
            health_y = self.rect.y - 40 + camera_offset[1]
            
            # bcakground bar (merah)
            pygame.draw.rect(surface, (255, 0, 0), (health_x, health_y, health_width, health_height))
            
            # health bar (hijau)
            health_percent = max(0, min(1, self.health / self.max_health))  # Pastikan nilai antara 0-1
            pygame.draw.rect(surface, (0, 255, 0), 
                            (health_x, health_y, int(health_width * health_percent), health_height))
            
            # border untuk health bar
            pygame.draw.rect(surface, (0, 0, 0), 
                            (health_x, health_y, health_width, health_height), 2)
                        
            # gambar text nama dan health di atas health bar
            name_font = pygame.font.Font(None, 24)
            
            # menambahkan indikator hit counter
            hit_counter_text = f" [{self.hit_counter}/{self.hits_to_flinch}]" if self.hit_counter > 0 else ""
            name_text = name_font.render(f"GOLLUX - {self.health}/{self.max_health} HP{hit_counter_text}", True, (255, 255, 255))
            name_rect = name_text.get_rect(midbottom=(health_x + health_width // 2, health_y - 5))
            surface.blit(name_text, name_rect)
