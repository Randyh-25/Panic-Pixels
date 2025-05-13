import pygame
import random
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        
        self.menu_music = pygame.mixer.Sound("assets/sound/bg/menu.ogg")
        self.menu_music.set_volume(0.5)  # Set default volume
        
        self.splash_sound = pygame.mixer.Sound("assets/sound/spl/spl.wav")
        
        self.footsteps = []
        for i in range(1, 22):
            sound_path = os.path.join("assets", "sound", "steps", "dirt", f"Steps_dirt-{i:03d}.ogg")
            try:
                step_sound = pygame.mixer.Sound(sound_path)
                step_sound.set_volume(0.2) 
                self.footsteps.append(step_sound)
            except pygame.error as e:
                print(f"Couldn't load footstep sound: {sound_path}")
                print(e)
        
        self.step_timer = 0
        self.step_delay = 300 
        self.last_step_time = 0
        
        self.current_music = None
        
    def play_menu_music(self):
        if self.current_music != "menu":
            pygame.mixer.stop() 
            self.menu_music.play(-1)
            self.current_music = "menu"
    
    def stop_menu_music(self):
        if self.current_music == "menu":
            self.menu_music.stop()
            self.current_music = None
            
    def play_splash_sound(self):
        self.splash_sound.play()
    
    def play_random_footstep(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_step_time >= self.step_delay:
            if self.footsteps:
                random.choice(self.footsteps).play()
                self.last_step_time = current_time
    
    def set_volume(self, volume):
        volume = max(0, min(volume / 100, 1))
        self.menu_music.set_volume(volume)
        self.splash_sound.set_volume(volume)
        
        for step in self.footsteps:
            step.set_volume(volume * 0.2) 