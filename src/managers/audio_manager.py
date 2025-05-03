import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.music_volume = 0.5
        self.sfx_volume = 0.5

    def load_music(self, music_file):
        pygame.mixer.music.load(music_file)

    def play_music(self, loop=-1):
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(loop)

    def stop_music(self):
        pygame.mixer.music.stop()

    def load_sound(self, sound_file):
        return pygame.mixer.Sound(sound_file)

    def play_sound(self, sound, loop=0):
        sound.set_volume(self.sfx_volume)
        sound.play(loop)

    def set_music_volume(self, volume):
        self.music_volume = volume
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, volume):
        self.sfx_volume = volume