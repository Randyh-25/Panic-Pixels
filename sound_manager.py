import pygame
import random
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        # Load music files
        self.menu_music = os.path.join('assets', 'sound', 'bg', 'menu.ogg')
        self.desert_music = os.path.join('assets', 'sound', 'bg', '1.ogg')
        
        # Load sound effects
        self.splash_sound = pygame.mixer.Sound(os.path.join('assets', 'sound', 'spl', 'spl.wav'))
        
        # Load footstep sounds
        self.footstep_sounds = []
        footstep_dir = os.path.join('assets', 'sound', 'steps', 'dirt')
        for i in range(1, 6):
            filename = f"Steps_dirt-00{i}.ogg"
            path = os.path.join(footstep_dir, filename)
            if os.path.exists(path):
                sound = pygame.mixer.Sound(path)
                sound.set_volume(0.2)
                self.footstep_sounds.append(sound)
        
        self.volume = 50
        self.set_volume(self.volume)
        
    def set_volume(self, volume):
        self.volume = volume / 100.0
        pygame.mixer.music.set_volume(self.volume)
        for sound in self.footstep_sounds:
            sound.set_volume(self.volume * 0.3)
        self.splash_sound.set_volume(self.volume)
        
    def play_menu_music(self):
        pygame.mixer.music.load(self.menu_music)
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely
        
    def play_gameplay_music(self, map_type='desert'):
        if map_type == 'desert':
            pygame.mixer.music.load(self.desert_music)
        # Add other map music options here in the future
        pygame.mixer.music.play(-1)  # Loop indefinitely
        
    def stop_gameplay_music(self):
        pygame.mixer.music.fadeout(1000)  # Fade out over 1 second
        
    def stop_menu_music(self):
        pygame.mixer.music.fadeout(500)
        
    def play_splash_sound(self):
        self.splash_sound.play()
        
    def play_random_footstep(self):
        if self.footstep_sounds:
            random.choice(self.footstep_sounds).play()