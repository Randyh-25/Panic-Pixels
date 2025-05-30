import pygame
import random
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()  # Inisialisasi mixer pygame untuk audio
        
        # Load file musik background
        self.menu_music = os.path.join('assets', 'sound', 'bg', 'menu.ogg')
        self.desert_music = os.path.join('assets', 'sound', 'bg', '1.ogg')
        
        # Load efek suara splash
        self.splash_sound = pygame.mixer.Sound(os.path.join('assets', 'sound', 'spl', 'spl.wav'))
        
        # Load efek suara UI (hover dan click)
        self.ui_hover_sound = self.load_sound(os.path.join('assets', 'sound', 'ui', 'select.ogg'))
        self.ui_click_sound = self.load_sound(os.path.join('assets', 'sound', 'ui', 'selected.ogg'))
        
        # Load suara langkah kaki dari folder steps/dirt
        self.footstep_sounds = []
        footstep_dir = os.path.join('assets', 'sound', 'steps', 'dirt')
        for i in range(1, 6):
            filename = f"Steps_dirt-00{i}.ogg"
            path = os.path.join(footstep_dir, filename)
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.2)  # Set volume awal langkah kaki
                self.footstep_sounds.append(sound)
        
        # Load suara kematian dan level up pemain
        self.player_death_sound = self.load_sound(os.path.join("assets", "sound", "cowboy", "death.ogg"))
        self.player_levelup_sound = self.load_sound(os.path.join("assets", "sound", "cowboy", "lvlup.ogg"))
        
        # Load partner throw sound effects
        self.partner_throw_sounds = []
        for i in range(2):
            throw_sound = self.load_sound(os.path.join("assets", "sound", "partner", f"throw{i}.ogg"))
            if throw_sound:
                throw_sound.set_volume(0.2)  # Increased volume from 0.1 to 0.3
                self.partner_throw_sounds.append(throw_sound)
                
        # Load Boss Gollux sound effects
        self.gollux_walk_sounds = []
        for i in range(1, 3):
            walk_sound = self.load_sound(os.path.join("assets", "sound", "boss-gollux", f"walk ({i}).ogg"))
            if walk_sound:
                walk_sound.set_volume(0.3)  # Volume langkah Gollux
                self.gollux_walk_sounds.append(walk_sound)
        
        self.gollux_attack_sounds = []
        for i in range(1, 7):
            attack_sound = self.load_sound(os.path.join("assets", "sound", "boss-gollux", f"attack ({i}).ogg"))
            if attack_sound:
                attack_sound.set_volume(0.6)  # Volume serangan Gollux
                self.gollux_attack_sounds.append(attack_sound)
        
        self.gollux_death_sound = self.load_sound(os.path.join("assets", "sound", "boss-gollux", "death.ogg"))
        if self.gollux_death_sound:
            self.gollux_death_sound.set_volume(0.7)  # Volume kematian Gollux

        # Set volume default untuk efek pemain
        if self.player_death_sound:
            self.player_death_sound.set_volume(0.5)
        if self.player_levelup_sound:
            self.player_levelup_sound.set_volume(0.7)
        
        self.volume = 50  # Volume awal (dalam persen)
        self.set_volume(self.volume)  # Terapkan volume ke semua suara
    
    # Fungsi untuk mencoba memuat sound dan menangani error jika gagal
    def load_sound(self, path):
        try:
            return pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Error loading sound: {path}")
            print(e)
            return None

    # Set volume global dan semua efek suara terkait
    def set_volume(self, volume):
        self.volume = volume / 100.0  # Konversi persen ke skala 0–1
        pygame.mixer.music.set_volume(self.volume)  # Volume musik latar
        for sound in self.footstep_sounds:
            sound.set_volume(self.volume * 0.3)
        self.splash_sound.set_volume(self.volume)
        
        # Volume untuk suara UI
        if self.ui_hover_sound:
            self.ui_hover_sound.set_volume(self.volume * 0.5)
        if self.ui_click_sound:
            self.ui_click_sound.set_volume(self.volume * 0.5)
    
    # Mainkan musik menu secara loop
    def play_menu_music(self):
        pygame.mixer.music.load(self.menu_music)
        pygame.mixer.music.play(-1)  # -1 = repeat selamanya
        
    # Mainkan musik gameplay berdasarkan tipe map
    def play_gameplay_music(self, map_type='desert'):
        if map_type == 'desert':
            pygame.mixer.music.load(self.desert_music)
        # Map lain bisa ditambahkan di sini
        pygame.mixer.music.play(-1)
    
    # Hentikan musik gameplay dengan fade out
    def stop_gameplay_music(self):
        pygame.mixer.music.fadeout(1000)
    
    # Hentikan musik menu dengan fade out
    def stop_menu_music(self):
        pygame.mixer.music.fadeout(500)
    
    # Mainkan suara splash (efek air, darah, dll)
    def play_splash_sound(self):
        self.splash_sound.play()
    
    # Mainkan suara langkah kaki acak
    def play_random_footstep(self):
        if self.footstep_sounds:
            random.choice(self.footstep_sounds).play()
    
    # Mainkan suara ketika player mati
    def play_player_death(self):
        if self.player_death_sound:
            self.player_death_sound.play()
    
    # Mainkan suara ketika player naik level
    def play_player_levelup(self):
        if self.player_levelup_sound:
            self.player_levelup_sound.play()
    
    # Mainkan efek hover saat kursor di atas tombol
    def play_ui_hover(self):
        if self.ui_hover_sound:
            self.ui_hover_sound.play()
    
    # Mainkan efek klik saat tombol ditekan
    def play_ui_click(self):
        if self.ui_click_sound:
            self.ui_click_sound.play()
    
    def play_victory_sound(self):
        """Play victory fanfare when player wins"""
        try:
            victory_sound = self.load_sound("assets/sound/bg/victory.ogg")
            victory_sound.set_volume(self.volume / 100.0)
            victory_sound.play()
        except:
            print("Error playing victory sound")
    
    def play_random_partner_throw(self, partner_type="eagle"):
        """Play a random throw sound effect for the partner"""
        if self.partner_throw_sounds:  # Removed partner_type check to ensure it plays
            random.choice(self.partner_throw_sounds).play()
    
    def play_gollux_walk(self):
        """Play random walk sound for Gollux"""
        if self.gollux_walk_sounds:
            random.choice(self.gollux_walk_sounds).play()
    
    def play_gollux_attack(self):
        """Play random attack sound for Gollux"""
        if self.gollux_attack_sounds:
            random.choice(self.gollux_attack_sounds).play()
    
    def play_gollux_death(self):
        """Play death sound for Gollux"""
        if self.gollux_death_sound:
            self.gollux_death_sound.play()
    
    def play_gold_sound(self):
        """Play sound effect for gold/money transactions"""
        try:
            # Try to load and play the gold sound from the assets directory
            gold_sound_path = os.path.join("assets", "sound", "ui", "coin.ogg")
            if os.path.exists(gold_sound_path):
                gold_sound = pygame.mixer.Sound(gold_sound_path)
                gold_sound.set_volume(self.volume / 100.0)  # Apply the current volume setting
                gold_sound.play()
            else:
                # Fallback to UI click sound if dedicated gold sound doesn't exist
                self.play_ui_click()
        except Exception as e:
            print(f"Error playing gold sound: {e}")
            # As a last resort, use the UI click sound
            if hasattr(self, 'play_ui_click'):
                self.play_ui_click()

