import pygame
from settings import WHITE, BLACK
from utils import load_game_data 
from settings import load_font 

def render_text_with_border(font, text, text_color, border_color):
    # Render the main text
    text_surface = font.render(text, True, text_color)
    
    # Create a slightly larger surface for the border
    final_surface = pygame.Surface((text_surface.get_width() + 2, text_surface.get_height() + 2), pygame.SRCALPHA)
    
    # Render border by offsetting the text in 8 directions
    for dx, dy in [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]:
        border_text = font.render(text, True, border_color)
        final_surface.blit(border_text, (dx + 1, dy + 1))
    
    # Draw the main text on top
    final_surface.blit(text_surface, (1, 1))
    
    return final_surface

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
        self.icon_width = 32  # Smaller icon size
        self.icon_height = 32  # Keep it square
        self.icon = pygame.transform.scale(self.icon, (self.icon_width, self.icon_height))
        
        # Posisi (dibawah health bar)
        self.x = 10
        self.y = 45
        
        # Font untuk money
        self.font = load_font(32)
        
    def draw(self, screen, player_session_money):
        # Draw icon
        screen.blit(self.icon, (self.x, self.y))
        
        # Load saved money and add current session money
        saved_money, _ = load_game_data()
        total_money = saved_money + player_session_money
        
        # Draw money amount with border
        money_text = render_text_with_border(self.font, f": {total_money}", WHITE, BLACK)
        # Calculate vertical center alignment
        text_y = self.y + (self.icon_height - money_text.get_height()) // 2
        screen.blit(money_text, (
            self.x + self.icon_width + 5,
            text_y
        ))

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
        self.font = load_font(20)  # Slightly smaller font for better fit
        
        # Adjust text positioning
        self.text_margin_bottom = 30  # Increased space between text and XP bar

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
        
        # Draw level text with border
        level_text = render_text_with_border(self.font, f"Level {level}", WHITE, BLACK)
        text_x = 10
        text_y = self.y - self.text_margin_bottom
        screen.blit(level_text, (text_x, text_y))
        
        # Draw XP text with border
        xp_text = render_text_with_border(self.font, f"{current_xp}/{max_xp} XP", WHITE, BLACK)
        xp_x = self.bg_width - xp_text.get_width() - 10
        xp_y = self.y - self.text_margin_bottom
        screen.blit(xp_text, (xp_x, xp_y))