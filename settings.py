# Ukuran default window
WIDTH, HEIGHT = 1366, 768

# Jumlah frame per detik (frame rate)
FPS = 60

# Definisi warna dalam format RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)

# Status fullscreen (True artinya layar penuh)
FULLSCREEN = True

# Resolusi saat ini (mengacu ke ukuran WIDTH dan HEIGHT)
CURRENT_RESOLUTION = (WIDTH, HEIGHT)

# Nilai volume awal (dalam persen)
VOLUME = 50

# Daftar resolusi yang tersedia untuk dipilih di pengaturan
RESOLUTIONS = [
    ('1280x720', (1280, 720)),
    ('1366x768', (1366, 768)),
    ('1920x1080', (1920, 1080)),
    ('2560x1440', (2560, 1440)),
    ('3840x2160', (3840, 2160)),
]

# Import modul pygame dan pygame_menu
import pygame
import pygame_menu
import os

# Path ke font khusus yang digunakan
FONT_PATH = "assets/font/PixelifySans-VariableFont_wght.ttf"

def load_font(size):
    """Fungsi untuk memuat font khusus dengan ukuran tertentu"""
    try:
        return pygame.font.Font(FONT_PATH, size)  # Load dari file
    except:
        # Jika gagal, gunakan font default dari sistem
        print(f"Warning: Could not load font {FONT_PATH}, using system default")
        return pygame.font.SysFont(None, size)

# Variabel global untuk status fullscreen dan resolusi saat ini
fullscreen = [FULLSCREEN]
current_resolution = CURRENT_RESOLUTION

def settings_menu(screen, main_menu_callback):
    """Fungsi untuk menampilkan menu pengaturan"""
    resolutions = RESOLUTIONS

    def toggle_fullscreen(value):
        """Fungsi untuk mengaktifkan/menonaktifkan fullscreen"""
        fullscreen[0] = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()  # Sembunyikan pilihan resolusi saat fullscreen
        else:
            pygame.display.set_mode(current_resolution)
            resolution_selector.show()

    def change_resolution(_, res):
        """Fungsi untuk mengubah resolusi saat tidak fullscreen"""
        global current_resolution
        if not fullscreen[0]:
            current_resolution = res
            pygame.display.set_mode(res)

    # Buat menu pengaturan menggunakan pygame_menu
    menu = pygame_menu.Menu('Settings', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    
    # Tambahkan selector untuk memilih resolusi
    resolution_selector = menu.add.selector('Resolution: ', resolutions, onchange=change_resolution)
    if fullscreen[0]:
        resolution_selector.hide()  # Sembunyikan jika mode fullscreen aktif

    # Tambahkan toggle switch untuk fullscreen
    menu.add.toggle_switch('Fullscreen: ', fullscreen[0], onchange=toggle_fullscreen)

    # Tambahkan slider untuk pengaturan volume
    menu.add.range_slider('Master Volume: ', default=VOLUME, range_values=(0, 100), increment=1,
                          onchange=lambda value: print(f"Volume set to {value}"))

    # Tombol untuk kembali ke menu utama
    menu.add.button('Back', main_menu_callback)

    # Jalankan menu
    menu.mainloop(screen)
