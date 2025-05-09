# 🎮 Too Many Pixels

**Too Many Pixels** is a fast-paced 2D survival shooter game developed with Python and Pygame. Dive into a pixelated desert world, fend off waves of enemies, gain experience, earn coins, level up, and survive as long as you can with the help of your smart AI partner.

## 🚀 Features

- ✅ **Solo Gameplay**: Control your character in an open desert battlefield with responsive controls.
- 🤖 **AI Partner**: An intelligent ally who helps by auto-shooting nearby enemies.
- 💥 **Projectile Pooling**: Optimized bullet system for efficient performance.
- 🌟 **Level Up System**: Collect XP to level up and trigger level-up effects.
- 💸 **In-Game Economy**: Earn coins by defeating enemies and collecting experience.
- ⚔️ **Enemy Spawning**: Dynamic enemy system with capped limit for smooth difficulty scaling.
- 🎨 **Polished UI**: Health bar, XP bar, and money display on-screen.
- 🌫️ **Visual Effects**: Particle system and death transition with blur + fade-out.
- 🔊 **Audio Manager**: Full sound integration with music and sound effects.
- 🧩 **Game Menus**: Splash screen, main menu, settings, pause menu, and game over screen using `pygame_menu`.
- 💾 **Save System**: Saves player name, coin total, and high score.

---

## 🎮 Controls

| Key         | Action                   |
|-------------|--------------------------|
| `Arrow Keys` / `WASD` | Move player |
| `ESC`       | Pause menu               |

---

## 🛠️ Tech Stack

- **Language**: Python 3.x
- **Libraries**: 
  - `pygame`
  - `pygame_menu`
- **Game Architecture**:
  - Modular design with clean separation: `player.py`, `enemy.py`, `projectile.py`, `maps.py`, `ui.py`, `sound_manager.py`, and more.

---

## 🧠 How It Works

- **Camera System**: Follows the player in a large map world.
- **Object Pooling**: Preloads and reuses projectile instances for performance.
- **AI Targeting**: Finds the nearest enemy within radius and shoots using partner AI.
- **Death Handling**: On zero health, game transitions with blur effect and fade-out to score screen.
- **XP and Leveling**: XP bar grows with kills; levels grant visual effects and XP cap increases.


