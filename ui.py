import pygame
import os
from settings import WIDTH, HEIGHT, WHITE, BLACK
from utils import load_game_data 
from settings import load_font 

def render_text_with_border(font, text, text_color, border_color):
    text_surface = font.render(text, True, text_color)
    final_surface = pygame.Surface((text_surface.get_width() + 2, text_surface.get_height() + 2), pygame.SRCALPHA)
    
    for dx, dy in [(-1,-1), (0,-1), (1,-1), (-1,0), (1,0), (-1,1), (0,1), (1,1)]:
        border_text = font.render(text, True, border_color)
        final_surface.blit(border_text, (dx + 1, dy + 1))
    
    final_surface.blit(text_surface, (1, 1))
    return final_surface

class HealthBar:
    def __init__(self):
        self.box = pygame.image.load("assets/UI/profile/health-bar-box.png").convert_alpha()
        self.bar = pygame.image.load("assets/UI/profile/health-bar.png").convert_alpha()
        
        self.box_width = 192
        self.box_height = 30
        self.box = pygame.transform.scale(self.box, (self.box_width, self.box_height))
        
        self.bar_width = 156
        self.bar_height = 20
        self.bar = pygame.transform.scale(self.bar, (self.bar_width, self.bar_height))
        
        self.x = 10
        self.y = 10
        
        self.bar_x_offset = (self.box_width - self.bar_width) // 2
        self.bar_y_offset = (self.box_height - self.bar_height) // 2

    def draw(self, screen, current_health, max_health):
        screen.blit(self.box, (self.x, self.y))
        
        health_ratio = max(0, min(current_health / max_health, 1))
        fill_width = int(self.bar_width * health_ratio)
        
        if fill_width > 0:
            health_bar = pygame.Surface((fill_width, self.bar_height), pygame.SRCALPHA)
            health_bar.blit(self.bar, (0, 0), (0, 0, fill_width, self.bar_height))
            screen.blit(health_bar, (
                self.x + self.bar_x_offset, 
                self.y + self.bar_y_offset
            ))

class MoneyDisplay:
    def __init__(self):
        self.icon = pygame.image.load("assets/UI/level/money.png").convert_alpha()
        
        self.icon_width = 32
        self.icon_height = 32
        self.icon = pygame.transform.scale(self.icon, (self.icon_width, self.icon_height))
        
        self.x = 10
        self.y = 45
        
        self.font = load_font(32)
        
    def draw(self, screen, player_session_money):
        screen.blit(self.icon, (self.x, self.y))
        
        saved_money, _, _ = load_game_data()
        total_money = saved_money + player_session_money
        
        money_text = render_text_with_border(self.font, f": {total_money}", WHITE, BLACK)
        text_y = self.y + (self.icon_height - money_text.get_height()) // 2
        screen.blit(money_text, (
            self.x + self.icon_width + 5,
            text_y
        ))

class XPBar:
    def __init__(self, screen_width, screen_height):
        self.bg = pygame.image.load("assets/UI/level/lvl.bg.png").convert_alpha()
        self.fill = pygame.image.load("assets/UI/level/lvl.fill.png").convert_alpha()
        
        self.bg_width = screen_width
        self.bg_height = 14
        self.fill_width = screen_width - 20
        self.fill_height = 14
        
        self.bg = pygame.transform.scale(self.bg, (self.bg_width, self.bg_height))
        self.fill = pygame.transform.scale(self.fill, (self.fill_width, self.fill_height))
        
        self.x = 0
        self.y = screen_height - self.bg_height
        
        self.fill_x_offset = (self.bg_width - self.fill_width) // 2
        self.fill_y_offset = (self.bg_height - self.fill_height) // 2
        
        self.font = load_font(20)
        
        self.text_margin_bottom = 30

    def draw(self, screen, current_xp, max_xp, level, max_width=None):
        if max_width is None:
            max_width = self.bg_width
            
        # Scale background and fill to viewport width
        scaled_bg = pygame.transform.scale(self.bg, (max_width, self.bg_height))
        scaled_fill = pygame.transform.scale(self.fill, (max_width - 20, self.fill_height))
        
        screen.blit(scaled_bg, (self.x, self.y))
        
        xp_ratio = max(0, min(current_xp / max_xp, 1))
        current_fill_width = int((max_width - 20) * xp_ratio)
        
        if current_fill_width > 0:
            fill_surface = pygame.Surface((current_fill_width, self.fill_height), pygame.SRCALPHA)
            fill_surface.blit(scaled_fill, (0, 0), (0, 0, current_fill_width, self.fill_height))
            screen.blit(fill_surface, (
                self.x + self.fill_x_offset,
                self.y + self.fill_y_offset
            ))
        
        # Draw text with proper positioning
        level_text = render_text_with_border(self.font, f"Level {level}", WHITE, BLACK)
        text_x = self.x + 10
        text_y = self.y - self.text_margin_bottom
        screen.blit(level_text, (text_x, text_y))
        
        xp_text = render_text_with_border(self.font, f"{current_xp}/{max_xp} XP", WHITE, BLACK)
        xp_x = self.x + max_width - xp_text.get_width() - 10
        xp_y = self.y - self.text_margin_bottom
        screen.blit(xp_text, (xp_x, xp_y))

class SplitScreenUI:
    def __init__(self, screen_width, screen_height):
        self.health_bar1 = HealthBar()
        self.health_bar2 = HealthBar()
        self.health_bar2.x = screen_width - 200  # Tetap di pojok kanan atas
        self.health_bar2.y = 10                  # Pastikan di atas
        
        self.xp_bar1 = XPBar(screen_width // 2, screen_height)  # Half width for player 1
        self.xp_bar2 = XPBar(screen_width // 2, screen_height)  # Half width for player 2
        self.xp_bar2.x = screen_width // 2  # Position for player 2
        
        self.money_display = MoneyDisplay()  # Shared money display
        
        # Simpan variabel screen_width untuk digunakan dalam draw_split
        self.screen_width = screen_width
        self.screen_height = screen_height
    
    def draw(self, screen, player1, player2):
        self.health_bar1.draw(screen, player1.health, player1.max_health)
        self.health_bar2.draw(screen, player2.health, player2.max_health)
        self.xp_bar1.draw(screen, player1.xp, player1.max_xp, player1.level)
        self.xp_bar2.draw(screen, player2.xp, player2.max_xp, player2.level)
        total_session_money = player1.session_money + player2.session_money
        self.money_display.draw(screen, total_session_money)

    def draw_split(self, screen, player1, player2, split_mode):
        if split_mode:
            # Left side UI (Player 1)
            self.health_bar1.x = 10
            self.health_bar1.y = 10
            self.health_bar1.draw(screen, player1.health, player1.max_health)
            self.xp_bar1.draw(screen, player1.xp, player1.max_xp, player1.level, self.screen_width//2)
            
            # Right side UI (Player 2)
            self.health_bar2.draw(screen, player2.health, player2.max_health)
            self.xp_bar2.x = self.screen_width // 2
            # PERBAIKI DI SINI: gunakan self.screen_width//2
            self.xp_bar2.draw(screen, player2.xp, player2.max_xp, player2.level, self.screen_width//2)
            
            # Shared money display in center
            total_session_money = player1.session_money + player2.session_money
            self.money_display.draw(screen, total_session_money)
        else:
            self.draw(screen, player1, player2)

class InteractionButton:
    def __init__(self):
        self.frames = []
        self.load_frames()
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15  # seconds between frames
        self.is_visible = False
        self.target_entity = None
        
    def load_frames(self):
        button_path = os.path.join("assets", "UI", "btn")
        try:
            self.frames.append(pygame.image.load(os.path.join(button_path, "E0.png")).convert_alpha())
            self.frames.append(pygame.image.load(os.path.join(button_path, "E1.png")).convert_alpha())
        except pygame.error as e:
            print(f"Error loading button frames: {e}")
            
    def update(self, dt):
        if not self.is_visible:
            return
            
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def show(self, target_entity):
        self.is_visible = True
        self.target_entity = target_entity
        
    def hide(self):
        self.is_visible = False
        self.target_entity = None
        
    def draw(self, surface, camera_offset):
        if not self.is_visible or not self.target_entity or not self.frames:
            return
        
        current_image = self.frames[self.current_frame]
        
        # Position the button above the target entity
        button_x = self.target_entity.rect.centerx - current_image.get_width() // 2
        button_y = self.target_entity.rect.top - current_image.get_height() - 10
        
        surface.blit(current_image, (button_x + camera_offset[0], button_y + camera_offset[1]))

class DevilShop:
    def __init__(self):
        self.is_open = False
        
    def open(self):
        self.is_open = True
        print("Devil shop opened!")  # Placeholder for now
        
    def close(self):
        self.is_open = False
        print("Devil shop closed!")  # Placeholder for now
        
    def update(self, events):
        if not self.is_open:
            return
        
        # Process shop events here (future implementation)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.close()
                
    def draw(self, surface):
        if not self.is_open:
            return
            
        # Placeholder shop UI
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent background
        
        font = pygame.font.SysFont(None, 48)
        text = font.render("Devil Shop (Coming Soon)", True, (255, 255, 255))
        text_rect = text.get_rect(center=(surface.get_width()//2, surface.get_height()//2))
        
        surface.blit(overlay, (0, 0))
        surface.blit(text, text_rect)