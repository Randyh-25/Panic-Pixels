import pygame_menu
import os
from settings import WIDTH, HEIGHT  # Tambahkan impor ini

# File untuk menyimpan skor tertinggi
HIGHEST_SCORE_FILE = "highest_score.txt"

def pause_menu(screen, main_menu_callback):
    menu = pygame_menu.Menu('Paused', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.button('Resume', lambda: None)  # Resume game
    menu.add.button('Main Menu', main_menu_callback)  # Go back to main menu
    menu.mainloop(screen)

def highest_score_menu(screen, current_score, main_menu_callback, replay_callback):
    # Baca skor tertinggi dari file
    if os.path.exists(HIGHEST_SCORE_FILE):
        with open(HIGHEST_SCORE_FILE, 'r') as file:
            highest_score = int(file.read())
    else:
        highest_score = 0

    # Perbarui skor tertinggi jika skor saat ini lebih tinggi
    if current_score > highest_score:
        highest_score = current_score
        with open(HIGHEST_SCORE_FILE, 'w') as file:
            file.write(str(highest_score))

    # Tampilkan menu skor tertinggi
    menu = pygame_menu.Menu('Game Over', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.label(f'Your Score: {current_score}')
    menu.add.label(f'Highest Score: {highest_score}')
    menu.add.button('Replay', replay_callback)  # Replay the game
    menu.add.button('Main Menu', main_menu_callback)  # Go back to main menu
    menu.mainloop(screen)