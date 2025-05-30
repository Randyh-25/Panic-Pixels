<div align="center">

# 🎮 Too Many Pixels
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-Latest-green.svg)](https://www.pygame.org/)
[![Version](https://img.shields.io/badge/Version-1.0-orange.svg)]()
</div>

## 📖 Deskripsi Proyek

**Too Many Pixels** adalah game survival shooter 2D berbasis Python dan Pygame. Pemain mengendalikan karakter pixel art di dunia gurun, bertahan dari gelombang musuh, mengumpulkan XP, uang, dan melakukan upgrade. Game ini mendukung mode solo dan co-op split-screen, serta menghadirkan berbagai fitur seperti partner AI, boss battle, efek partikel, dan sistem ekonomi dalam game.

---

## 📦 Dependensi Paket

Aplikasi ini membutuhkan beberapa library berikut untuk dijalankan:

- **Python 3.x**
- **pygame** (engine utama game dan rendering)
- **pygame_menu** (untuk sistem menu dan GUI)
- (Opsional) **numpy** (untuk beberapa operasi matematis, jika digunakan)
- (Opsional) **soundfile** atau library audio lain jika ada fitur tambahan

Instalasi dapat dilakukan dengan:

```bash
pip install -r requirements.txt
```

---

## ▶️ Cara Menjalankan Aplikasi & Cara Bermain

### Menjalankan Game

1. **Clone repository:**
    ```bash
    git clone https://github.com/yourusername/TooMuchPixels.git
    cd TooMuchPixels
    ```
2. **Install dependensi:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Jalankan game:**
    ```bash
    python main.py
    ```

### Cara Bermain

- **Gerakkan karakter:** `WASD` atau `Arrow Keys`
- **Skill spesial:** `1` `2` `3`
- **Pause/Menu:** `ESC`
- **Cheat Console:** `` ` `` (backtick)
- **Co-op:** Pilih mode split-screen di menu utama

Kalahkan musuh, kumpulkan XP dan uang, lakukan upgrade, dan bertahan selama mungkin!

---

## 📊 UML Class Diagram

Berikut adalah gambaran sederhana UML class diagram untuk proyek ini:



---

## 👥 Kontributor Pengembangan

- **Randy Hendriyawan** – Game loop utama,	main.py, settings.py, sound_manager.py, solo.py, coop.py  
- **M. Riveldo Hermawan P.** – Entitas Player dan fungsinya	Player.py, Player2.py, partner.py, Player_animations.py
- **Ola Anggela Rosita** – 	Entitas pendukung gameplay	enemy.py, Bi_enemy.py, gollux.py, devil.py
- **Muhammad Fadhel** – Fungsi skill dan draw map	projectile.py, Bi_projectile.py, skill.py, experience.py, maps.py

---

## 📚 Referensi

- [Pygame Documentation](https://www.pygame.org/docs/)
- [Pygame Menu](https://pygame-menu.readthedocs.io/)
- [Python Official Documentation](https://docs.python.org/3/)
- [Pixel Art Tutorials](https://lospec.com/)
- Sumber asset dan audio bebas hak cipta dari [OpenGameArt](https://opengameart.org/) dan [Itch.io](https://itch.io/)

---

<div align="center">
  <i>Made with ❤️ and a lot of pixels</i>
</div>


