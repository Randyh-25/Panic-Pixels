import pygame

class Map:
    def __init__(self, map_file):
        self.image = pygame.image.load(map_file).convert()
        self.width, self.height = self.image.get_size()

    def draw(self, screen, camera):
        # Gambar peta secara berulang (infinite scrolling)
        for x in range(-self.width, screen.get_width() + self.width, self.width):
            for y in range(-self.height, screen.get_height() + self.height, self.height):
                screen.blit(self.image, camera.apply(pygame.Rect(x, y, self.width, self.height)))