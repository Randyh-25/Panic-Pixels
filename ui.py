import pygame

class HealthBar:
    def __init__(self):
        self.empty_bar = pygame.image.load("assets/UI/profile/hempty.png").convert_alpha()
        self.full_bar = pygame.image.load("assets/UI/profile/hfull.png").convert_alpha()
        
        # Atur ukuran bar
        self.bar_width = 400
        self.bar_height = 150
        self.empty_bar = pygame.transform.scale(self.empty_bar, (self.bar_width, self.bar_height))
        self.full_bar = pygame.transform.scale(self.full_bar, (self.bar_width, self.bar_height))
        
        # Posisi bar
        self.x = 10
        self.y = 10

    def draw(self, screen, current_health, max_health):
        # Gambar bar kosong
        screen.blit(self.empty_bar, (self.x, self.y))
        
        # Hitung lebar bar penuh berdasarkan health
        health_ratio = max(0, min(current_health / max_health, 1))
        fill_width = int(self.bar_width * health_ratio)
        
        # Crop dan gambar bar penuh dengan alpha channel
        if fill_width > 0:
            health_bar = pygame.Surface((fill_width, self.bar_height), pygame.SRCALPHA)
            health_bar.blit(self.full_bar, (0, 0), (0, 0, fill_width, self.bar_height))
            screen.blit(health_bar, (self.x, self.y))