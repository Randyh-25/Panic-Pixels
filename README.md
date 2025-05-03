# Arcade Game

## Overview
Arcade Game is a 2D action game where players control a character to survive against waves of enemies. Players can collect experience points, manage health, and utilize various weapons to defeat enemies.

## Project Structure
The project is organized into several directories and modules:

- **assets/**: Contains all game assets including audio, fonts, and images.
  - **audio/**: Organized into `music` and `sfx` subdirectories for sound effects and background music.
  - **fonts/**: Contains font files used in the game.
  - **images/**: Organized into subdirectories for `enemies`, `player`, `projectiles`, and `ui` elements.

- **src/**: Contains the source code for the game.
  - **core/**: Contains the main game logic and settings.
    - `game.py`: Main game loop and initialization.
    - `settings.py`: Configuration settings such as screen dimensions and color constants.
  - **entities/**: Contains classes for game entities.
    - `enemy.py`: Defines the Enemy class.
    - `player.py`: Defines the Player class.
    - `projectile.py`: Defines the Projectile class.
  - **managers/**: Contains classes for managing game assets and levels.
    - `asset_manager.py`: Manages loading and accessing game assets.
    - `audio_manager.py`: Manages audio playback.
    - `level_manager.py`: Handles level transitions.
  - **ui/**: Contains classes for user interface elements.
    - `hud.py`: Manages the Heads-Up Display (HUD).
    - `screens.py`: Defines different game screens.
  - **utils/**: Contains utility functions.
    - `helpers.py`: Utility functions for collision detection and random number generation.
  - `main.py`: Entry point of the game.

- **tests/**: Contains unit tests for the game.
  - `test_enemy.py`: Unit tests for the Enemy class.
  - `test_player.py`: Unit tests for the Player class.
  - `test_projectile.py`: Unit tests for the Projectile class.

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd arcade-game
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the game:
   ```
   python src/main.py
   ```

## Gameplay
- Use the arrow keys or WASD to move the player character.
- Collect experience points by defeating enemies and picking up experience items.
- Manage your health and score displayed on the HUD.

## Contributing
This project is open for contributions. Please fork the repository and submit a pull request for any changes or enhancements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.