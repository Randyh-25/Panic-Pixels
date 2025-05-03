import pygame
from settings import WHITE  # Import color constants

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

class MoneyDisplay:
    def __init__(self):
        # Load money icon
        self.icon = pygame.image.load("assets/UI/level/money.png").convert_alpha()
        
        # Set ukuran icon
        self.icon_width = 50
        self.icon_height = 50
        self.icon = pygame.transform.scale(self.icon, (self.icon_width, self.icon_height))
        
        # Posisi (dibawah health bar)
        self.x = 10
        self.y = 40  # Sesuaikan dengan posisi health bar
        
        # Font untuk money
        self.font = pygame.font.SysFont(None, 50)
        
    def draw(self, screen, money):
        # Draw icon
        screen.blit(self.icon, (self.x, self.y))
        
        # Draw money amount
        money_text = self.font.render(f": {money}", True, (255, 255, 255))
        screen.blit(money_text, (self.x + self.icon_width + 5, self.y + 2))  # +2 untuk center vertikal

class XPBar:
    def __init__(self, screen_width, screen_height):
        # Load images
        self.bg = pygame.image.load("assets/UI/level/lvl.bg.png").convert_alpha()
        self.fill = pygame.image.load("assets/UI/level/lvl.fill.png").convert_alpha()
        
        # Scale to screen width
        self.bg_width = screen_width
        self.bg_height = 14  # Double the original height
        self.fill_width = screen_width - 20  # Leave some padding
        self.fill_height = 14
        
        # Scale images
        self.bg = pygame.transform.scale(self.bg, (self.bg_width, self.bg_height))
        self.fill = pygame.transform.scale(self.fill, (self.fill_width, self.fill_height))
        
        # Position at bottom of screen
        self.x = 0
        self.y = screen_height - self.bg_height
        
        # Center fill in bg
        self.fill_x_offset = (self.bg_width - self.fill_width) // 2
        self.fill_y_offset = (self.bg_height - self.fill_height) // 2
        
        # Font for level display
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, screen, current_xp, max_xp, level):
        # Draw background bar
        screen.blit(self.bg, (self.x, self.y))
        
        # Calculate fill width based on XP
        xp_ratio = max(0, min(current_xp / max_xp, 1))
        current_fill_width = int(self.fill_width * xp_ratio)
        
        if current_fill_width > 0:
            # Create fill surface with alpha channel
            fill_surface = pygame.Surface((current_fill_width, self.fill_height), pygame.SRCALPHA)
            # Draw portion of fill bar
            fill_surface.blit(self.fill, (0, 0), (0, 0, current_fill_width, self.fill_height))
            # Draw fill bar
            screen.blit(fill_surface, (
                self.x + self.fill_x_offset,
                self.y + self.fill_y_offset
            ))
        
        # Draw level text
        level_text = self.font.render(f"Level {level}", True, WHITE)
        text_x = 10
        text_y = self.y - 20
        screen.blit(level_text, (text_x, text_y))
        
        # Draw XP text
        xp_text = self.font.render(f"{current_xp}/{max_xp} XP", True, WHITE)
        xp_x = self.bg_width - xp_text.get_width() - 10
        xp_y = self.y - 20
        screen.blit(xp_text, (xp_x, xp_y))