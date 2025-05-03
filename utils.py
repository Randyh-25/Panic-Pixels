import os
import pickle
import pygame_menu
from settings import WIDTH, HEIGHT

SAVE_FILE = "game.dat"

def save_game_data(money=0, highest_score=0):
    game_data = {
        'money': money,
        'highest_score': highest_score
    }
    with open(SAVE_FILE, 'wb') as file:
        pickle.dump(game_data, file)

def load_game_data():
    try:
        with open(SAVE_FILE, 'rb') as file:
            game_data = pickle.load(file)
            return game_data['money'], game_data['highest_score']
    except (FileNotFoundError, EOFError, KeyError):
        return 0, 0  # Default values if file doesn't exist or is corrupted

def pause_menu(screen, main_menu_callback):
    menu = pygame_menu.Menu('Paused', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.button('Resume', lambda: None)  # Resume game
    menu.add.button('Main Menu', main_menu_callback)  # Go back to main menu
    menu.mainloop(screen)

def highest_score_menu(screen, player, main_menu_callback, replay_callback):
    # Load existing data
    _, current_highest_score = load_game_data()
    
    # Calculate final score
    final_score = (player.level * 1000) + player.xp + player.money
    
    # Update highest score if necessary
    if final_score > current_highest_score:
        current_highest_score = final_score
    
    # Save both money and highest score
    save_game_data(player.money, current_highest_score)

    menu = pygame_menu.Menu('Game Over', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.label(f'Level Reached: {player.level}')
    menu.add.label(f'XP Gained: {player.xp}')
    menu.add.label(f'Money Earned: {player.money}')
    menu.add.label(f'Final Score: {final_score}')
    menu.add.label(f'Highest Score: {current_highest_score}')
    menu.add.button('Replay', replay_callback)
    menu.add.button('Main Menu', main_menu_callback)
    menu.mainloop(screen)