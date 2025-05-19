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
                   game_data.get('player_name', "")) 
    except (FileNotFoundError, EOFError, KeyError):
        return 0, 0, "" 

def pause_menu(screen, main_menu_callback):
    from main import create_themed_menu
    
    menu = create_themed_menu('Paused', WIDTH, HEIGHT)
    menu.add.button('Resume', menu.disable)  # This will close the pause menu
    menu.add.button('Main Menu', main_menu_callback)  
    menu.mainloop(screen)

def highest_score_menu(screen, player, main_menu_callback, replay_callback):
    from main import create_themed_menu, sound_manager
    
    menu = create_themed_menu('Game Over', WIDTH, HEIGHT)
    menu.add.label(f'Level Reached: {player.level}')
    menu.add.label(f'XP Gained: {player.xp}')
    menu.add.label(f'Session Money: {player.session_money}')
    menu.add.label(f'Total Money: {total_money}')
    menu.add.label(f'Final Score: {final_score}')
    menu.add.label(f'Highest Score: {current_highest_score}')
    menu.add.button('Replay', replay_callback)
    menu.add.button('Main Menu', main_menu_callback)
    menu.mainloop(screen)

def save_splitscreen_data(money=0):
    game_data = {
        'money': money,
        'mode': 'splitscreen'
    }
    with open(SAVE_FILE, 'wb') as file:
        pickle.dump(game_data, file)

def splitscreen_game_over(screen, player1, player2, main_menu_callback, replay_callback):
    from main import create_themed_menu, sound_manager
    
    menu = create_themed_menu('Game Over', WIDTH, HEIGHT)
    menu.add.label(f'Player 1 Level: {player1.level}')
    menu.add.label(f'Player 2 Level: {player2.level}')
    menu.add.label(f'Session Money: {total_session_money}')
    menu.add.label(f'Total Money: {total_money}')
    menu.add.button('Replay', replay_callback)
    menu.add.button('Main Menu', main_menu_callback)
    menu.mainloop(screen)