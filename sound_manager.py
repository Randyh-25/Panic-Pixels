import pygame

class SoundManager:
    def __init__(self):
        # Initialize mixer
        pygame.mixer.init()
        
        # Load menu music
        self.menu_music = pygame.mixer.Sound("assets/sound/bg/menu.wav")
        self.menu_music.set_volume(0.5)  # Set default volume
        
        # Load splash sound
        self.splash_sound = pygame.mixer.Sound("assets/sound/spl/spl.wav")
        
        # Track music state
        self.current_music = None
        
    def play_menu_music(self):
        if self.current_music != "menu":
            pygame.mixer.stop()  # Stop any currently playing music
            self.menu_music.play(-1)  # -1 means loop indefinitely
            self.current_music = "menu"
    
    def stop_menu_music(self):
        if self.current_music == "menu":
            self.menu_music.stop()
            self.current_music = None
            
    def play_splash_sound(self):
        self.splash_sound.play()
    
    def set_volume(self, volume):
        # Volume should be between 0 and 1
        volume = max(0, min(volume / 100, 1))
        self.menu_music.set_volume(volume)
        self.splash_sound.set_volume(volume)