import pygame

class HealthBar:
    def __init__(self):
        # Load images
        self.box = pygame.image.load("assets/UI/profile/health-bar-box.png").convert_alpha()
        self.bar = pygame.image.load("assets/UI/profile/health-bar.png").convert_alpha()
        
        # Ukuran Box Health
        self.box_width = 192
        self.box_height = 30
        self.box = pygame.transform.scale(self.box, (self.box_width, self.box_height))
        
        # Ukuran Health Bar
        self.bar_width = 156
        self.bar_height = 20
        self.bar = pygame.transform.scale(self.bar, (self.bar_width, self.bar_height))
        
        # Posisi Box Health
        self.x = 10
        self.y = 10
        
        # Menghitung offset untuk menempatkan health bar di tengah box
        self.bar_x_offset = (self.box_width - self.bar_width) // 2
        self.bar_y_offset = (self.box_height - self.bar_height) // 2

    def draw(self, screen, current_health, max_health):
        # Draw the box
        screen.blit(self.box, (self.x, self.y))
        
        # Menghitung lebar health bar berdasarkan rasio kesehatan saat ini terhadap kesehatan maksimum
        health_ratio = max(0, min(current_health / max_health, 1))
        fill_width = int(self.bar_width * health_ratio)
        
        # Only draw the health bar if there's health remaining
        if fill_width > 0:
            # Create a surface for the health bar with alpha channel
            health_bar = pygame.Surface((fill_width, self.bar_height), pygame.SRCALPHA)
            # Draw the portion of the health bar
            health_bar.blit(self.bar, (0, 0), (0, 0, fill_width, self.bar_height))
            # Draw the health bar inside the box with proper offset
            screen.blit(health_bar, (
                self.x + self.bar_x_offset, 
                self.y + self.bar_y_offset
            ))