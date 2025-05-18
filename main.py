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
    sound_manager.stop_menu_music()
    
    if mode == "solo":
        solo.main(screen, clock, sound_manager, main_menu)
    elif mode == "split_screen":
        coop.split_screen_main(screen, clock, sound_manager, main_menu)

def settings_menu():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Settings', min(WIDTH, pygame.display.get_surface().get_width()),
                          min(HEIGHT, pygame.display.get_surface().get_height()),
                          theme=theme)
    
    def toggle_fullscreen(value):
        global FULLSCREEN
        FULLSCREEN = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()
        else:
            pygame.display.set_mode(CURRENT_RESOLUTION)
            resolution_selector.show()

    def change_resolution(_, res):
        global CURRENT_RESOLUTION
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
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Quit Confirmation', WIDTH, HEIGHT, theme=theme)
    menu.add.label('Are you sure you want to quit?')
    menu.add.button('Yes', pygame.quit)
    menu.add.button('No', main_menu)
    menu.mainloop(screen)

def main_menu():
    sound_manager.play_menu_music()
    
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Main Menu', 
                          min(WIDTH, pygame.display.get_surface().get_width()),
                          min(HEIGHT, pygame.display.get_surface().get_height()),
                          theme=theme)
    
    saved_money, highest_score, player_name = load_game_data()
    
    if player_name:
        menu.add.label(f"Welcome, {player_name}!")
        menu.add.label(f"Total Money: {saved_money}")
    
    menu.add.button('Start', game_mode_menu)
    menu.add.button('Settings', settings_menu)
    menu.add.button('Quit', quit_confirmation)
    menu.mainloop(screen)

def game_mode_menu():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Game Mode', WIDTH, HEIGHT, theme=theme)
    menu.add.button('Solo', lambda: start_game("solo"))
    menu.add.button('Co-op Multiplayer', lambda: start_game("split_screen"))
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def player_name_screen():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu(
        'Welcome to "Too Many Pixels"', 
        WIDTH, 
        HEIGHT,
        theme=theme
    )
    
    player_name = [""]
    
    def save_name():
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