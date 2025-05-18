import pygame
import os
from settings import WIDTH, HEIGHT, WHITE, BLACK, FONT_PATH
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
        self.selected_item = 0
        self.items = [
            {"name": "Health Potion", "price": 50, "desc": "Restore 20 health"},
            {"name": "Max Health Up", "price": 200, "desc": "+10 max health"},
            {"name": "Speed Boost", "price": 150, "desc": "+10% movement speed"},
            {"name": "Damage Boost", "price": 300, "desc": "+15% damage"}
        ]
        
        # Shop UI elements
        self.border_color = (255, 215, 0)  # Gold color for border
        self.bg_color = (40, 40, 40, 220)  # Dark semi-transparent background
        self.title_color = (255, 255, 255)
        self.text_color = (200, 200, 200)
        self.highlight_color = (255, 215, 0)
        self.error_color = (255, 80, 80)
        
        # Position and size
        self.width = 500
        self.height = 400
        self.padding = 20
        self.item_height = 50
        self.message = ""
        self.message_timer = 0
        
        # Load fonts
        self.title_font = pygame.font.Font(FONT_PATH, 36)
        self.item_font = pygame.font.Font(FONT_PATH, 24)
        self.desc_font = pygame.font.Font(FONT_PATH, 18)
        
    def open(self):
        self.is_open = True
        self.selected_item = 0
        self.message = ""
        
    def close(self):
        self.is_open = False
        
    def update(self, events):
        if not self.is_open:
            return
        
        # Handle message timer
        if self.message:
            self.message_timer += 1
            if self.message_timer > 120:  # 2 seconds at 60 FPS
                self.message = ""
                self.message_timer = 0
        
        # Process input for menu navigation
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                elif event.key == pygame.K_UP:
                    self.selected_item = (self.selected_item - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected_item = (self.selected_item + 1) % len(self.items)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.purchase_item()
    
    def purchase_item(self):
        # This would be connected to the player's money system in a real implementation
        self.message = f"Purchased {self.items[self.selected_item]['name']}!"
        self.message_timer = 0
        
    def draw(self, surface):
        if not self.is_open:
            return
        
        # Calculate position (centered on screen)
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        x = (screen_width - self.width) // 2
        y = (screen_height - self.height) // 2
        
        # Create a semi-transparent overlay just for the menu area
        shop_bg = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        shop_bg.fill(self.bg_color)
        surface.blit(shop_bg, (x, y))
        
        # Draw gold border
        pygame.draw.rect(surface, self.border_color, 
                         (x, y, self.width, self.height), 3, border_radius=10)
        
        # Draw devil shop title
        title = self.title_font.render("Devil's Shop", True, self.title_color)
        title_rect = title.get_rect(midtop=(x + self.width//2, y + self.padding))
        surface.blit(title, title_rect)
        
        # Draw items
        item_start_y = y + title_rect.height + self.padding * 2
        for i, item in enumerate(self.items):
            # Determine if this item is selected
            is_selected = i == self.selected_item
            item_color = self.highlight_color if is_selected else self.text_color
            
            # Draw selection indicator
            if is_selected:
                selection_rect = pygame.Rect(
                    x + self.padding // 2,
                    item_start_y + i * (self.item_height + 5),
                    self.width - self.padding,
                    self.item_height
                )
                pygame.draw.rect(surface, (60, 60, 60), selection_rect, border_radius=5)
                pygame.draw.rect(surface, self.border_color, selection_rect, 2, border_radius=5)
            
            # Item name and price
            item_text = f"{item['name']} - ${item['price']}"
            item_surface = self.item_font.render(item_text, True, item_color)
            surface.blit(item_surface, (
                x + self.padding * 2,
                item_start_y + i * (self.item_height + 5) + 10
            ))
            
            # Description below if selected
            if is_selected:
                desc_surface = self.desc_font.render(item['desc'], True, self.text_color)
                surface.blit(desc_surface, (
                    x + self.padding * 2,
                    item_start_y + i * (self.item_height + 5) + 35
                ))
        
        # Draw bottom instructions
        instruction_y = y + self.height - self.padding - 20
        instructions = self.desc_font.render("↑/↓: Select  |  Enter: Buy  |  ESC: Close", True, self.text_color)
        instructions_rect = instructions.get_rect(center=(x + self.width//2, instruction_y))
        surface.blit(instructions, instructions_rect)
        
        # Draw message if any
        if self.message:
            message_surf = self.item_font.render(self.message, True, self.highlight_color)
            message_rect = message_surf.get_rect(midbottom=(x + self.width//2, instruction_y - 20))
            surface.blit(message_surf, message_rect)

class MiniMap:
    def __init__(self, map_width, map_height, screen_width, screen_height):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Mini map dimensions and position
        self.width = 180
        self.height = 180
        self.padding = 10
        self.x = screen_width - self.width - self.padding
        self.y = self.padding
        
        # Mini map scale factors
        self.scale_x = self.width / map_width
        self.scale_y = self.height / map_height
        
        # Create the mini map surface with semi-transparency
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Entity colors
        self.player_color = (0, 255, 0)          # Green for player
        self.enemy_color = (255, 0, 0)           # Red for enemies
        self.devil_color = (150, 0, 0)           # Dark red for devil outline
        self.devil_color_inner = (0, 0, 0)       # Black for devil inner circle
        
        # Entity sizes
        self.player_size = 5
        self.enemy_size = 3
        self.devil_size = 7
    
    def update_map_size(self, map_width, map_height):
        """Update map size if needed"""
        self.map_width = map_width
        self.map_height = map_height
        self.scale_x = self.width / map_width
        self.scale_y = self.height / map_height
    
    def draw(self, screen, player, enemies=None, devil=None):
        # Clear the surface with translucent dark background
        self.surface.fill((20, 20, 20, 180))
        
        # Draw border
        pygame.draw.rect(self.surface, (200, 200, 200), 
                         (0, 0, self.width, self.height), 2)
        
        # Draw enemies
        if enemies:
            for enemy in enemies:
                if not enemy.is_dying:  # Only show active enemies
                    mini_x = int(enemy.rect.centerx * self.scale_x)
                    mini_y = int(enemy.rect.centery * self.scale_y)
                    pygame.draw.circle(self.surface, self.enemy_color, (mini_x, mini_y), self.enemy_size)
        
        # Draw devil if exists
        if devil and not getattr(devil, "fading_out", False):
            mini_x = int(devil.rect.centerx * self.scale_x)
            mini_y = int(devil.rect.centery * self.scale_y)
            # Draw devil as a larger circle with two colors
            pygame.draw.circle(self.surface, self.devil_color, (mini_x, mini_y), self.devil_size)
            pygame.draw.circle(self.surface, self.devil_color_inner, (mini_x, mini_y), self.devil_size - 2)
        
        # Draw player (draw last so it's on top)
        mini_x = int(player.rect.centerx * self.scale_x)
        mini_y = int(player.rect.centery * self.scale_y)
        pygame.draw.circle(self.surface, self.player_color, (mini_x, mini_y), self.player_size)
        
        # Draw the mini map on the screen
        screen.blit(self.surface, (self.x, self.y))