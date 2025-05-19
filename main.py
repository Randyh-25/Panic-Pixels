import pygame
import sys
import pygame_menu
from settings import *
from utils import pause_menu, highest_score_menu, load_game_data, save_game_data
from ui import render_text_with_border
from settings import load_font
from sound_manager import SoundManager
import solo
import coop

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  
pygame.display.set_caption("Too Many Pixels")
clock = pygame.time.Clock()
sound_manager = SoundManager()

# Custom sound engine for pygame_menu
class SoundEngine(pygame_menu.sound.Sound):
    def __init__(self, sound_manager):
        super().__init__()
        self.sound_manager = sound_manager
        
    def play_click_sound(self) -> None:
        self.sound_manager.play_ui_click()
        
    def play_key_add_sound(self) -> None:
        self.sound_manager.play_ui_hover()
        
    def play_open_menu_sound(self) -> None:
        self.sound_manager.play_ui_click()
        
    def play_close_menu_sound(self) -> None:
        self.sound_manager.play_ui_click()

# Helper function to create themed menu with sounds
def create_themed_menu(title, width, height):
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    # Add stronger title border styling
    theme.title_background_color = (0, 0, 0, 200)  # More opaque black
    theme.title_font_shadow = True
    theme.title_font_shadow_color = (0, 0, 0)
    theme.title_font_shadow_offset = 3  # Increased offset for more visibility
    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
    theme.title_font_size = 36
    theme.title_font_antialias = True
    theme.title_font_color = (255, 255, 255)  # White text
    
    # Add thicker border
    theme.title_offset = (5, 5)
    theme.title_padding = (10, 10)
    
    # Set outline color to solid black
    theme.title_close_button_background_color = (0, 0, 0)
    theme.title_floating = False  # Ensures the title has a solid background
    
    # Add border to menu
    theme.border_width = 4  # Increase border width for more visibility
    theme.border_color = (0, 0, 0)
    
    # Stronger title border
    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_UNDERLINE_TITLE
    theme.title_underline_width = 3
    theme.title_underline_color = (0, 0, 0)
    
    # Set background image for menu
    theme.background_color = pygame_menu.baseimage.BaseImage(
        image_path='assets/UI/bg.png',
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL
    )
    
    menu = pygame_menu.Menu(
        title, 
        width,
        height,
        theme=theme,
        onclose=pygame_menu.events.CLOSE
    )
    
    # Add sound engine to menu
    menu.set_sound(SoundEngine(sound_manager))
    
    # Remove the custom decorator code that's causing the error
    
    return menu

# Modified functions to use the new themed menu
def splash_screen():
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    title_font = load_font(72)
    studio_font = load_font(36)
    title_text = title_font.render("Too Many Pixels", True, WHITE)
    studio_text = studio_font.render("D'King Studio", True, WHITE)
    
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    studio_rect = studio_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    
    sound_manager.play_splash_sound()
    
    for alpha in range(255, 0, -5):
        screen.fill(BLACK)
        fade_surface.set_alpha(alpha)
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    pygame.time.delay(2000)
    
    for alpha in range(0, 255, 5):
        screen.fill(BLACK)
        fade_surface.set_alpha(alpha)
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)

def start_game(mode):
    sound_manager.play_ui_click()
    sound_manager.stop_menu_music()
    
    if mode == "solo":
        solo.main(screen, clock, sound_manager, main_menu)
    elif mode == "split_screen":
        coop.split_screen_main(screen, clock, sound_manager, main_menu)

def settings_menu():
    menu = create_themed_menu(
        'Settings', 
        min(WIDTH, pygame.display.get_surface().get_width()),
        min(HEIGHT, pygame.display.get_surface().get_height())
    )
    
    def toggle_fullscreen(value):
        global FULLSCREEN
        sound_manager.play_ui_click()
        FULLSCREEN = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()
        else:
            pygame.display.set_mode(CURRENT_RESOLUTION)
            resolution_selector.show()

    def change_resolution(_, res):
        global CURRENT_RESOLUTION
        sound_manager.play_ui_click()
        if not FULLSCREEN:
            CURRENT_RESOLUTION = res
            pygame.display.set_mode(res)
            menu.resize(min(res[0], pygame.display.get_surface().get_width()),
                       min(res[1], pygame.display.get_surface().get_height()))

    def change_volume(value):
        global VOLUME
        VOLUME = value
        sound_manager.set_volume(value)

    resolution_selector = menu.add.selector('Resolution: ', RESOLUTIONS, onchange=change_resolution)
    if FULLSCREEN:
        resolution_selector.hide()
    
    menu.add.toggle_switch('Fullscreen: ', FULLSCREEN, onchange=toggle_fullscreen)
    menu.add.range_slider('Master Volume: ', default=VOLUME, range_values=(0, 100), 
                         increment=1, onchange=change_volume)
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def quit_confirmation():
    menu = create_themed_menu('Quit Confirmation', WIDTH, HEIGHT)
    menu.add.label('Are you sure you want to quit?')
    menu.add.button('Yes', pygame.quit)
    menu.add.button('No', main_menu)
    menu.mainloop(screen)

def main_menu():
    sound_manager.play_menu_music()
    
    menu = create_themed_menu(
        'Main Menu', 
        min(WIDTH, pygame.display.get_surface().get_width()),
        min(HEIGHT, pygame.display.get_surface().get_height())
    )
    
    saved_money, highest_score, player_name = load_game_data()
    
    if player_name:
        menu.add.label(f"Welcome, {player_name}!")
        menu.add.label(f"Total Money: {saved_money}")
    
    menu.add.button('Start', game_mode_menu)
    menu.add.button('Settings', settings_menu)
    menu.add.button('Quit', quit_confirmation)
    menu.mainloop(screen)

def game_mode_menu():
    menu = create_themed_menu('Game Mode', WIDTH, HEIGHT)
    menu.add.button('Solo', lambda: start_game("solo"))
    menu.add.button('Co-op Multiplayer', lambda: start_game("split_screen"))
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def player_name_screen():
    menu = create_themed_menu(
        'Welcome to "Too Many Pixels"', 
        WIDTH, 
        HEIGHT
    )
    
    player_name = [""]
    
    def save_name():
        sound_manager.play_ui_click()
        if player_name[0].strip():
            save_game_data(0, 0, player_name[0])
            main_menu()
    
    def name_changed(value):
        player_name[0] = value
    
    menu.add.label("Please enter your name")
    menu.add.text_input(' ', default='', onchange=name_changed)
    menu.add.button('Confirm', save_name)
    menu.mainloop(screen)
    
if __name__ == "__main__":
    splash_screen()
    _, _, player_name = load_game_data()
    if not player_name:
        player_name_screen()
    else:
        main_menu()