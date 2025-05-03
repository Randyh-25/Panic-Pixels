import pygame
import os

class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def load_image(self, name):
        path = os.path.join('assets', 'images', name)
        image = pygame.image.load(path).convert_alpha()
        self.images[name] = image
        return image

    def get_image(self, name):
        return self.images.get(name)

    def load_sound(self, name):
        path = os.path.join('assets', 'audio', 'sfx', name)
        sound = pygame.mixer.Sound(path)
        self.sounds[name] = sound
        return sound

    def get_sound(self, name):
        return self.sounds.get(name)

    def load_font(self, name, size):
        path = os.path.join('assets', 'fonts', name)
        font = pygame.font.Font(path, size)
        self.fonts[name] = font
        return font

    def get_font(self, name):
        return self.fonts.get(name)