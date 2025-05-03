import pygame

class SoundManager:
    def __init__(self):
        # Initialize mixer
        pygame.mixer.init()
        
        # Load menu music
        self.menu_music = pygame.mixer.Sound("assets/sound/bg/menu.wav")
        
        # Track music state
        self.current_music = None
        self.is_playing = False
        
    def play_menu_music(self):
        if self.current_music != "menu":
            # Stop any currently playing music
            pygame.mixer.stop()
            # Play menu music
            self.menu_music.play(-1)  # -1 means loop indefinitely
            self.current_music = "menu"
            self.is_playing = True
    
    def stop_menu_music(self):
        if self.current_music == "menu":
            self.menu_music.stop()
            self.current_music = None
            self.is_playing = False
    
    def set_volume(self, volume):
        # Volume should be between 0 and 1
        volume = max(0, min(volume / 100, 1))
        self.menu_music.set_volume(volume)