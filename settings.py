WIDTH, HEIGHT = 1366, 768

FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)

FULLSCREEN = True
CURRENT_RESOLUTION = (WIDTH, HEIGHT)
VOLUME = 50

RESOLUTIONS = [
    ('1280x720', (1280, 720)),
    ('1366x768', (1366, 768)),
    ('1920x1080', (1920, 1080)),
    ('2560x1440', (2560, 1440)),
    ('3840x2160', (3840, 2160)),
]

import pygame
import pygame_menu
import os

FONT_PATH = "assets/font/PixelifySans-VariableFont_wght.ttf"

def load_font(size):
    """Load the Pixelify Sans font with specified size"""
    try:
        return pygame.font.Font(FONT_PATH, size)
    except:
        print(f"Warning: Could not load font {FONT_PATH}, using system default")
        return pygame.font.SysFont(None, size)
    
fullscreen = [FULLSCREEN]
current_resolution = CURRENT_RESOLUTION

def settings_menu(screen, main_menu_callback):
    resolutions = RESOLUTIONS

    def toggle_fullscreen(value):
        fullscreen[0] = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()
        else:
            pygame.display.set_mode(current_resolution)
            resolution_selector.show()

    def change_resolution(_, res):
        global current_resolution
        if not fullscreen[0]:
            current_resolution = res
            pygame.display.set_mode(res)

    menu = pygame_menu.Menu('Settings', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    resolution_selector = menu.add.selector('Resolution: ', resolutions, onchange=change_resolution)
    if fullscreen[0]:
        resolution_selector.hide()
    menu.add.toggle_switch('Fullscreen: ', fullscreen[0], onchange=toggle_fullscreen)
    menu.add.range_slider('Master Volume: ', default=VOLUME, range_values=(0, 100), increment=1,
                          onchange=lambda value: print(f"Volume set to {value}"))
    menu.add.button('Back', main_menu_callback)
    menu.mainloop(screen)
