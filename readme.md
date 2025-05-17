<div align="center">
  
# 🎮 Too Many Pixels

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-Latest-green.svg)](https://www.pygame.org/)
[![Version](https://img.shields.io/badge/Version-0.1-orange.svg)]()

**A fast-paced 2D survival shooter where every pixel counts!**

[What is This Game](#-what-is-this-game) • [Game Mechanics](#-game-mechanics) • [OOP Implementation](#-oop-implementation) • [Assets Used](#-assets-used) • [Controls](#-controls) • [Installation](#-installation) • [Tech Stack](#%EF%B8%8F-tech-stack) • [Future Roadmap](#-future-roadmap)

</div>

## 📜 What is This Game

**Too Many Pixels** is a high-octane 2D survival shooter developed with Python and Pygame. Players navigate a pixelated desert world, battling endless waves of enemies while collecting experience points and currency. The game features both solo and split-screen cooperative gameplay, with an AI partner that assists in combat. With its roguelike elements, procedural difficulty scaling, and special events like the Devil's appearance, Too Many Pixels offers a challenging and dynamic experience for pixel art enthusiasts and action game fans alike.

## 🎮 Game Mechanics

- **Survival Gameplay**: Survive waves of increasingly difficult enemies in an expansive map
- **Progression System**: Defeat enemies to gain XP and level up, increasing health and abilities
- **Combat**: AI-assisted combat with automatic projectile targeting for nearby threats
- **Economy**: Collect money from defeated enemies to unlock upgrades and abilities
- **Split-Screen Multiplayer**: Play cooperatively with a friend in local split-screen mode
- **Special Events**: The "Devil" appears periodically as a powerful ally that can eliminate enemies within its area of effect
- **Death & Respawn**: When players die, their session stats are recorded before returning to the menu
- **Environmental Effects**: Particle systems create atmospheric desert environments
- **Cheat System**: Hidden command console for debugging and special features

## 🧠 OOP Implementation

The game showcases the four pillars of Object-Oriented Programming:

### 1. Encapsulation
- **Player Classes** (`player.py`, `player2.py`): Encapsulate player properties and behaviors
- **Enemy Class** (`enemy.py`): Hides internal state and attack behaviors
- **UI Components** (`ui.py`): Encapsulates rendering logic and state

### 2. Inheritance
- **Sprite Inheritance**: All game entities inherit from `pygame.sprite.Sprite`
- **Devil Class** (`devil.py`): Extends base sprite functionality with specialized behaviors
- **Hit Effects** (`hit_effects.py`): RockHitEffect inherits from Sprite for animation system

### 3. Polymorphism
- **Update Methods**: Consistent `update()` interfaces across different entity types:
  - `Enemy.update()`, `Player.update()`, `Projectile.update()`, `ParticleSystem.update()`
- **Draw Methods**: Polymorphic rendering through consistent `draw()` interfaces

### 4. Abstraction
- **Camera System** (`player.py`): Abstracts complex viewport calculations
- **Sound Manager**: Provides high-level sound control without exposing implementation details
- **Particle System** (`particles.py`): Abstracts particle generation and lifecycle management

## 🎨 Assets Used

- **Character Sprites**:
  - Player characters with multiple animation states
  - Partner/companion sprites
  - Various enemy types with attack animations
  - Devil special character with FX effects
  
- **Environment**:
  - Desert map tileset (`assets/maps/desert/plain.png`)
  - Shadow effects and overlays
  
- **UI Elements**:
  - Health bars, XP bars, money displays
  - Menu backgrounds and buttons
  - Split-screen dividers
  
- **Effects**:
  - Particle effects for environment
  - Hit animations (`assets/enemy/collapse/`)
  - Level-up visual effects
  - Death transitions
  
- **Audio**:
  - Gameplay music with map-specific variations
  - Combat sound effects
  - UI feedback sounds

## 🎮 Controls

| Key             | Action                 |
|-----------------|------------------------|
| `Arrow Keys` / `WASD` | Move player     |
| `Mouse`         | Aim                   |
| `Left Click`    | Shoot                 |
| `Space`         | Special ability       |
| `ESC`           | Pause menu            |
| `Tab`           | View stats            |
| `` ` ``         | Toggle cheat console  |

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/TooMuchPixels.git

# Navigate to the game directory
cd TooMuchPixels

# Install dependencies
pip install -r requirements.txt

# Launch the game
python main.py
```

## 🛠️ Tech Stack

- **Core**: Python 3.x
- **Frameworks**: 
  - `pygame` - Game engine and rendering
  - `pygame_menu` - UI menu system
- **Architecture**:
  - Modular design with clean component separation
  - Entity-Component System for game object management
  - Optimized rendering pipeline for smooth performance

## 🚀 Future Roadmap

### Short Term (3 Months)
- **New Maps**: Add forest and dungeon environments with unique enemies
- **Weapon System**: Implement different weapon types with upgrade paths
- **Boss Battles**: Create challenging boss encounters at specified intervals
- **Online Multiplayer**: Basic networked gameplay support

### Mid Term (6 Months)
- **Character Classes**: Different playable characters with unique abilities
- **Skill Trees**: Deeper progression mechanics with branching upgrades
- **Procedural Map Generation**: Dynamic level creation for infinite replayability
- **Custom Game Modes**: Survival, wave-based, and challenge modes

### Long Term (12+ Months)
- **Mobile Port**: Android and iOS compatibility
- **Story Campaign**: Narrative-driven single-player experience
- **Workshop Support**: Community-created maps and mods
- **Cross-Platform Multiplayer**: Play across different devices

---

<div align="center">
  <i>Made with ❤️ and a lot of pixels</i>
</div>


