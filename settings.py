# settings.py
WIDTH, HEIGHT = 1280, 720
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)

import pygame
import pygame_menu

# Track fullscreen state and resolution
fullscreen = [True]  # Default to fullscreen
current_resolution = (WIDTH, HEIGHT)  # Gunakan tuple langsung

def settings_menu(screen, main_menu_callback):
    resolutions = [('1280x720', (1280, 720))]

    def toggle_fullscreen(value):
        fullscreen[0] = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()
        else:
            pygame.display.set_mode(current_resolution)  # Gunakan current_resolution langsung
            resolution_selector.show()

    def change_resolution(_, res):
        global current_resolution
        if not fullscreen[0]:
            current_resolution = res  # Perbarui current_resolution
            pygame.display.set_mode(res)

    menu = pygame_menu.Menu('Settings', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    resolution_selector = menu.add.selector('Resolution: ', resolutions, onchange=change_resolution)
    if fullscreen[0]:
        resolution_selector.hide()  # Hide resolution selector if fullscreen is active
    menu.add.toggle_switch('Fullscreen: ', fullscreen[0], onchange=toggle_fullscreen)
    menu.add.range_slider('Master Volume: ', default=50, range_values=(0, 100), increment=1,
                          onchange=lambda value: print(f"Volume set to {value}"))
    menu.add.button('Back', main_menu_callback)
    menu.mainloop(screen)
