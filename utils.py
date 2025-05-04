import os
import pickle
import pygame_menu
from settings import WIDTH, HEIGHT, load_font, FONT_PATH, BLACK, WHITE

SAVE_FILE = "game.dat"

def save_game_data(money=0, highest_score=0, player_name=""):
    game_data = {
        'money': money,
        'highest_score': highest_score,
        'player_name': player_name
    }
    with open(SAVE_FILE, 'wb') as file:
        pickle.dump(game_data, file)

def load_game_data():
    try:
        with open(SAVE_FILE, 'rb') as file:
            game_data = pickle.load(file)
            return (game_data['money'], 
                   game_data['highest_score'],
                   game_data.get('player_name', ""))  # Use get() with default value
    except (FileNotFoundError, EOFError, KeyError):
        return 0, 0, ""  # Return empty string for player_name if file doesn't exist

def pause_menu(screen, main_menu_callback):
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Paused', WIDTH, HEIGHT, theme=theme)
    menu.add.button('Resume', lambda: None)  # Resume game
    menu.add.button('Main Menu', main_menu_callback)  # Go back to main menu
    menu.mainloop(screen)

def highest_score_menu(screen, player, main_menu_callback, replay_callback):
    # Load existing data
    saved_money, current_highest_score, player_name = load_game_data()
    
    # Calculate total money
    total_money = saved_money + player.session_money
    
    # Calculate final score
    final_score = (player.level * 10) + player.xp
    
    # Update highest score if necessary
    if final_score > current_highest_score:
        current_highest_score = final_score
    
    # Save updated total money and highest score
    save_game_data(total_money, current_highest_score, player_name)

    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Game Over', WIDTH, HEIGHT, theme=theme)
    menu.add.label(f'Level Reached: {player.level}')
    menu.add.label(f'XP Gained: {player.xp}')
    menu.add.label(f'Session Money: {player.session_money}')
    menu.add.label(f'Total Money: {total_money}')
    menu.add.label(f'Final Score: {final_score}')
    menu.add.label(f'Highest Score: {current_highest_score}')
    menu.add.button('Replay', replay_callback)
    menu.add.button('Main Menu', main_menu_callback)
    menu.mainloop(screen)