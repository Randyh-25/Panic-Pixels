
import pygame
import sys
import pygame_menu
from settings import *
from utils import pause_menu, highest_score_menu, load_game_data, save_game_data
from ui import render_text_with_border
from settings import load_font
from sound_manager import SoundManager
import solo
import coop
import math
import random
from player_animations import PlayerAnimations

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  
pygame.display.set_caption("Too Much Pixels")
clock = pygame.time.Clock()
sound_manager = SoundManager()

# Inisialisasi animasi player sekali saja
player_anim = PlayerAnimations()
player_anim2 = PlayerAnimations()  # Untuk player kedua jika co-op

# Particle effects for menu background
class MenuParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(1, 3)
        self.color = (random.randint(180, 255), random.randint(180, 255), random.randint(180, 255))
        self.speed = random.uniform(0.2, 1.0)
        self.angle = random.uniform(0, 2 * math.pi)
        self.lifetime = random.randint(100, 200)
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.lifetime -= 1
        # Fade out effect
        if self.lifetime < 50:
            alpha = int((self.lifetime / 50) * 255)
            self.color = (*self.color[:3], alpha)
        
    def draw(self, surface):
        if self.lifetime > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

class MenuParticleSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.spawn_timer = 0
        
    def update(self):
        # Add new particles occasionally
        self.spawn_timer += 1
        if self.spawn_timer >= 5:  # Spawn every 5 frames
            self.spawn_timer = 0
            for _ in range(2):  # Spawn 2 particles at a time
                self.particles.append(MenuParticle(
                    random.randint(0, self.width),
                    random.randint(0, self.height)
                ))
        
        # Update existing particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
                
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

# Create menu background with particles
particle_system = MenuParticleSystem(WIDTH, HEIGHT)
menu_background = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# Custom sound engine for pygame_menu with enhanced feedback
class SoundEngine(pygame_menu.sound.Sound):
    def __init__(self, sound_manager):
        super().__init__()
        self.sound_manager = sound_manager
        
    def play_click_sound(self) -> None:
        self.sound_manager.play_ui_click()
        
    def play_key_add_sound(self) -> None:
        self.sound_manager.play_ui_hover()
        
    def play_open_menu_sound(self) -> None:
        self.sound_manager.play_ui_click()
        
    def play_close_menu_sound(self) -> None:
        self.sound_manager.play_ui_click()

# Enhanced widget effect - pulse effect for buttons
class PulseWidgetTransform(pygame_menu.widgets.core.Selection):
    def __init__(self):
        super().__init__()
        self.pulse_time = 0
        self.pulse_amplitude = 0.03  # Maximum scale factor
        self.pulse_frequency = 0.05  # Speed of pulse
        
    def draw(self, surface, widget):
        if widget.is_selected():
            # Create a pulsing effect when selected
            self.pulse_time += self.pulse_frequency
            scale_factor = 1.0 + self.pulse_amplitude * math.sin(self.pulse_time)
            
            # Create a copy of the original surface to apply effects
            if hasattr(widget, '_surface'):
                original_rect = widget.get_rect()
                
                # Calculate scaled dimensions
                scaled_width = int(original_rect.width * scale_factor)
                scaled_height = int(original_rect.height * scale_factor)
                
                # Center the scaled surface
                x_offset = (original_rect.width - scaled_width) // 2
                y_offset = (original_rect.height - scaled_height) // 2
                
                # Apply scaling
                surface_copy = pygame.transform.scale(widget._surface, (scaled_width, scaled_height))
                
                # Add glow effect
                glow_color = (255, 255, 0, 50)  # Subtle yellow glow
                glow = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                glow.fill(glow_color)
                surface_copy.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                
                # Draw the transformed surface
                surface.blit(surface_copy, (original_rect.x + x_offset, original_rect.y + y_offset))
                return True
                
        return False

# Helper function to create themed menu with enhanced visuals
def create_themed_menu(title, width, height):
    # Create a custom theme with pixel art style
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    # Enhanced title styling
    theme.title_background_color = (20, 20, 30, 220)
    theme.title_font_shadow = True
    theme.title_font_shadow_color = (0, 0, 0)
    theme.title_font_shadow_offset = 3
    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_SIMPLE
    theme.title_font_size = 45
    theme.title_font_antialias = True
    theme.title_font_color = (255, 230, 150)  # Warm gold color
    
    # Title positioning and decoration
    theme.title_offset = (5, 5)
    theme.title_padding = (15, 15)
    
    # Improved widget styling
    theme.widget_font_size = 36
    theme.widget_padding = (10, 15)
    theme.widget_margin = (0, 15)
    
    # Gunakan SimpleSelection sebagai fallback yang aman
    theme.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
    
    # Button styling
    theme.widget_font_color = (220, 220, 220)
    theme.selection_color = (255, 215, 0)
    theme.widget_selection_color = (255, 255, 150)
    
    # Menu background
    theme.background_color = pygame_menu.baseimage.BaseImage(
        image_path='assets/UI/bg.png',
        drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL,
        drawing_offset=(0, 0)
    )
    
    # Create decorated borders
    theme.border_width = 2
    theme.border_color = (255, 215, 0)  # Gold border
    
    # Title underline for style
    # theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_UNDERLINE_TITLE
    # theme.title_underline_width = 3
    # theme.title_underline_color = (255, 215, 0)  # Gold underline
    theme.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_NONE
    
    # Create menu with the enhanced theme
    menu = pygame_menu.Menu(
        title, 
        width,
        height,
        theme=theme,
        onclose=pygame_menu.events.CLOSE,
        center_content=True
    )
    
    # Add custom sound engine
    menu.set_sound(SoundEngine(sound_manager))
    
    return menu

# Modified splash screen with particle effects and smoother transitions
def splash_screen():
    particles = []
    
    # Create initial particles
    for _ in range(50):
        particles.append(MenuParticle(
            random.randint(0, WIDTH),
            random.randint(0, HEIGHT)
        ))
    
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    # Prepare text with better styling
    title_font = load_font(100)
    studio_font = load_font(48)
    subtext_font = load_font(24)
    
    title_text = title_font.render("Too Much Pixels", True, (255, 230, 150))
    studio_text = studio_font.render("D'King Studio", True, (200, 200, 200))
    subtext = subtext_font.render("Long Live D'King", True, (150, 150, 150))
    
    # Position text
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
    studio_rect = studio_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    subtext_rect = subtext.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    
    # Play splash sound
    sound_manager.play_splash_sound()
    
    # Fade in
    for alpha in range(255, 0, -3):
        screen.fill((10, 10, 15))  # Dark blue-black background
        
        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                particles.remove(particle)
                if len(particles) < 50:
                    particles.append(MenuParticle(
                        random.randint(0, WIDTH),
                        random.randint(0, HEIGHT)
                    ))
        
        # Draw text with shadow
        shadow_offset = 3
        shadow_color = (0, 0, 0, 100)
        
        # Draw shadows
        shadow_title = title_font.render("Too Much Pixels", True, shadow_color)
        shadow_studio = studio_font.render("D'King Studio", True, shadow_color)
        shadow_subtext = subtext_font.render("Long Live D'King", True, shadow_color)
        
        screen.blit(shadow_title, (title_rect.x + shadow_offset, title_rect.y + shadow_offset))
        screen.blit(shadow_studio, (studio_rect.x + shadow_offset, studio_rect.y + shadow_offset))
        screen.blit(shadow_subtext, (subtext_rect.x + shadow_offset, subtext_rect.y + shadow_offset))
        
        # Draw actual text
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(subtext, subtext_rect)
        
        # Apply fade
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)
    
    # Hold for a moment
    pygame.time.delay(2000)
    
    # Fade out
    for alpha in range(0, 255, 3):
        screen.fill((10, 10, 15))
        
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.lifetime <= 0:
                particles.remove(particle)
        
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(subtext, subtext_rect)
        
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        
        pygame.display.flip()
        clock.tick(60)

def start_game(mode):
    # Enhanced game start transition
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    # Play UI click with slight delay before fading
    sound_manager.play_ui_click()
    pygame.time.delay(200)
    
    for alpha in range(0, 255, 5):
        screen.fill((10, 10, 15))
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Stop menu music with proper transition
    sound_manager.stop_menu_music()
    
    if mode == "solo":
        solo.main(screen, clock, sound_manager, main_menu)
    elif mode == "split_screen":
        coop.split_screen_main(screen, clock, sound_manager, main_menu)

def settings_menu():
    menu = create_themed_menu(
        'Settings', 
        min(WIDTH, pygame.display.get_surface().get_width()),
        min(HEIGHT, pygame.display.get_surface().get_height())
    )
    
    def toggle_fullscreen(value):
        global FULLSCREEN
        sound_manager.play_ui_click()
        FULLSCREEN = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()
        else:
            pygame.display.set_mode(CURRENT_RESOLUTION)
            resolution_selector.show()

    def change_resolution(_, res):
        global CURRENT_RESOLUTION
        sound_manager.play_ui_click()
        if not FULLSCREEN:
            CURRENT_RESOLUTION = res
            pygame.display.set_mode(res)
            menu.resize(min(res[0], pygame.display.get_surface().get_width()),
                       min(res[1], pygame.display.get_surface().get_height()))

    def change_volume(value):
        global VOLUME
        VOLUME = value
        sound_manager.set_volume(value)

    # Section titles with decorative elements
    menu.add.label('• DISPLAY SETTINGS •', font_size=28, font_color=(255, 215, 0))
    menu.add.vertical_margin(10)
    resolution_selector = menu.add.selector('Resolution: ', RESOLUTIONS, onchange=change_resolution,
                                         font_size=28, selection_color=(255, 255, 150))
    if FULLSCREEN:
        resolution_selector.hide()
    
    menu.add.toggle_switch('Fullscreen: ', FULLSCREEN, onchange=toggle_fullscreen,
                        font_size=28, selection_color=(255, 255, 150))
    
    menu.add.vertical_margin(30)
    menu.add.label('• AUDIO SETTINGS •', font_size=28, font_color=(255, 215, 0))
    menu.add.vertical_margin(10)
    menu.add.range_slider('Master Volume: ', default=VOLUME, range_values=(0, 100), 
                       increment=5, onchange=change_volume,
                       font_size=28, slider_color=(255, 215, 0))
                       
    menu.add.vertical_margin(30)
    menu.add.button('Back to Main Menu', main_menu, font_size=32, 
                  background_color=(40, 40, 60))
    
    # Create dynamic background with particles during menu loop
    while menu.is_enabled():
        # Update particle system
        particle_system.update()
        
        # Draw background and particles first
        menu_background.fill((10, 10, 15, 200))  # Semi-transparent background
        particle_system.draw(menu_background)
        
        # Update menu with the background
        events = pygame.event.get()
        menu.update(events)
        menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def quit_confirmation():
    menu = create_themed_menu('Quit Game', WIDTH, HEIGHT)
    
    menu.add.vertical_margin(20)
    menu.add.label('Are you sure you want to exit the game?', font_size=40, 
                 font_color=(255, 255, 255), margin=(0, 30))
    menu.add.vertical_margin(20)
    
    # Create a more appealing button layout
    button_layout = menu.add.frame_h(500, 80)
    button_layout.pack(menu.add.button('Yes', pygame.quit, 
                                    font_size=36, 
                                    background_color=(170, 50, 50),
                                    border_width=2,
                                    border_color=(255, 150, 150)), 
                    align=pygame_menu.locals.ALIGN_CENTER)
                    
    button_layout.pack(menu.add.button('No', main_menu, 
                                    font_size=36,
                                    background_color=(50, 170, 50),
                                    border_width=2,
                                    border_color=(150, 255, 150)), 
                    align=pygame_menu.locals.ALIGN_CENTER)
    
    # Create dynamic background with particles during menu loop
    while menu.is_enabled():
        particle_system.update()
        
        menu_background.fill((10, 10, 15, 220))
        particle_system.draw(menu_background)
        
        events = pygame.event.get()
        menu.update(events)
        menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def draw_player_menu_animation(surface, solo_hover, coop_hover, frame_idx):
    # Perlambat animasi: ganti frame setiap 7 tick
    anim_speed = 7
    walk_anim = player_anim.animations['walk_down']
    walk_anim2 = player_anim2.animations['walk_down']
    frame = walk_anim[(frame_idx // anim_speed) % len(walk_anim)]
    frame2 = walk_anim2[(frame_idx // anim_speed) % len(walk_anim2)]

    # Perbesar sprite (misal 1.5x)
    scale_factor = 1.5
    frame = pygame.transform.scale(frame, (int(frame.get_width() * scale_factor), int(frame.get_height() * scale_factor)))
    frame2 = pygame.transform.scale(frame2, (int(frame2.get_width() * scale_factor), int(frame2.get_height() * scale_factor)))

    center_x = WIDTH // 2
    center_y = HEIGHT // 2 + 40

    if solo_hover:
        surface.blit(frame, (center_x - frame.get_width() // 2, center_y - frame.get_height() // 2))
    elif coop_hover:
        offset = 50  # Sedikit lebih lebar agar tidak bertumpuk
        surface.blit(frame, (center_x - frame.get_width() - offset//2, center_y - frame.get_height() // 2))
        surface.blit(frame2, (center_x + offset//2, center_y - frame2.get_height() // 2))

def main_menu():
    sound_manager.play_menu_music()
    
    menu = create_themed_menu(
        ' ', 
        min(WIDTH, pygame.display.get_surface().get_width()),
        min(HEIGHT, pygame.display.get_surface().get_height())
    )
    
    saved_money, highest_score, player_name = load_game_data()
    
    # Add animated logo
    logo_img = pygame.image.load('assets/UI/logo.png').convert_alpha() if os.path.exists('assets/UI/logo.png') else None
    if logo_img:
        logo_img = pygame.transform.scale(logo_img, (400, 150))
        menu.add.image(logo_img, scale=(1, 1), scale_smooth=True)
        menu.add.vertical_margin(20)
    
    # Player information: tampilkan langsung tanpa frame/container
    if player_name:
        menu.add.vertical_margin(150)
        menu.add.label(
            f"WELCOME, {player_name.upper()}",
            font_size=28,
            font_color=(255, 215, 0),
            font_shadow=True,
            font_shadow_color=(0, 0, 0),
            font_shadow_offset=2
        )
        
    
    # Button styling with improved visuals
    button_style = {
        'font_size': 42,
        'background_color': (40, 40, 60),
        'border_width': 2,
        'border_color': (255, 215, 0, 80),
        'cursor': pygame_menu.locals.CURSOR_HAND
    }
    
    menu.add.button('PLAY', game_mode_menu, **button_style)
    menu.add.vertical_margin(10)
    menu.add.button('SETTINGS', settings_menu, **button_style)
    menu.add.vertical_margin(10)
    menu.add.button('QUIT', quit_confirmation, **button_style)
    
    # Decorative footer
    menu.add.vertical_margin(50)
    menu.add.label("© 2025 D'King Studio", font_size=16, font_color=(150, 150, 150))
    
    # Create dynamic background with particles
    while menu.is_enabled():
        particle_system.update()
        
        menu_background.fill((10, 10, 15, 200))
        particle_system.draw(menu_background)
        
        events = pygame.event.get()
        menu.update(events)
        menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)

def game_mode_menu():
    menu = create_themed_menu('SELECT GAME MODE', WIDTH, HEIGHT)
    
    # Add descriptive info for each mode
    menu.add.vertical_margin(30)
    
    # Buat layout horizontal untuk menempatkan mode game bersebelahan
    # Gunakan ukuran yang lebih besar untuk menghindari masalah overflow
    mode_layout = menu.add.frame_h(WIDTH - 100, 350)
    
    # KOLOM KIRI: Mode Solo
    solo_frame = menu.add.frame_v(430, 300, background_color=(20, 20, 30, 150), border_width=2, border_color=(255, 215, 0))
    solo_frame.set_margin(20, 20)  # Tambahkan margin
    
    # Tambahkan ikon solo jika tersedia
    if os.path.exists('assets/UI/solo_icon.png'):
        solo_icon = pygame.image.load('assets/UI/solo_icon.png').convert_alpha()
        solo_icon = pygame.transform.scale(solo_icon, (100, 100))
        solo_frame.pack(menu.add.image(solo_icon), align=pygame_menu.locals.ALIGN_CENTER)
    
    solo_frame.pack(menu.add.label('SOLO ADVENTURE', font_size=36, font_color=(255, 215, 0)), align=pygame_menu.locals.ALIGN_CENTER)
    solo_frame.pack(menu.add.vertical_margin(10))
    
    # Split description into multiple lines for better fit
    solo_frame.pack(menu.add.label('Face the dangers alone', font_size=20), align=pygame_menu.locals.ALIGN_CENTER)
    solo_frame.pack(menu.add.label('in a quest for survival', font_size=20), align=pygame_menu.locals.ALIGN_CENTER)
    solo_frame.pack(menu.add.vertical_margin(20))
    
    solo_button = menu.add.button('START SOLO', lambda: start_game("solo"), 
                  font_size=28, 
                  background_color=(40, 40, 60),
                  border_width=2,
                  border_color=(255, 215, 0, 80))
    solo_frame.pack(solo_button, align=pygame_menu.locals.ALIGN_CENTER)
    
    # KOLOM KANAN: Mode Co-op
    coop_frame = menu.add.frame_v(430, 300, background_color=(20, 20, 30, 150), border_width=2, border_color=(255, 215, 0))
    coop_frame.set_margin(20, 20)  # Tambahkan margin
    
    # Tambahkan ikon co-op jika tersedia
    if os.path.exists('assets/UI/coop_icon.png'):
        coop_icon = pygame.image.load('assets/UI/coop_icon.png').convert_alpha()
        coop_icon = pygame.transform.scale(coop_icon, (100, 100))
        coop_frame.pack(menu.add.image(coop_icon), align=pygame_menu.locals.ALIGN_CENTER)
    
    coop_frame.pack(menu.add.label('CO-OP MULTIPLAYER', font_size=36, font_color=(255, 215, 0)), align=pygame_menu.locals.ALIGN_CENTER)
    coop_frame.pack(menu.add.vertical_margin(10))
    
    # Split description into multiple lines for better fit
    coop_frame.pack(menu.add.label('Team up with a friend', font_size=20), align=pygame_menu.locals.ALIGN_CENTER)
    coop_frame.pack(menu.add.label('in split-screen action', font_size=20), align=pygame_menu.locals.ALIGN_CENTER)
    coop_frame.pack(menu.add.vertical_margin(20))
    
    coop_button = menu.add.button('START CO-OP', lambda: start_game("split_screen"),
                  font_size=28,
                  background_color=(40, 40, 60),
                  border_width=2,
                  border_color=(255, 215, 0, 80))
    coop_frame.pack(coop_button, align=pygame_menu.locals.ALIGN_CENTER)
    
    # Pack keduanya ke dalam layout horizontal
    mode_layout.pack(solo_frame, align=pygame_menu.locals.ALIGN_LEFT)
    mode_layout.pack(coop_frame, align=pygame_menu.locals.ALIGN_RIGHT)
    
    # Tambahkan tombol kembali di bawah layout
    menu.add.vertical_margin(30)
    menu.add.button('Back to Main Menu', main_menu, 
                  font_size=28,
                  background_color=(60, 60, 80))
    
    # Variabel status hover
    mode_hover = {"solo": False, "coop": False}

    # --- Tambahkan event handler hover ---
    def on_solo_hover(selected, value):
        mode_hover["solo"] = selected
        mode_hover["coop"] = False

    def on_coop_hover(selected, value):
        mode_hover["solo"] = False
        mode_hover["coop"] = selected

    solo_button.set_onselect(lambda: on_solo_hover(True, None))
    coop_button.set_onselect(lambda: on_coop_hover(True, None))

    def reset_hover():
        mode_hover["solo"] = False
        mode_hover["coop"] = False

    frame_idx = 0
    while menu.is_enabled():
        particle_system.update()
        menu_background.fill((10, 10, 15, 200))
        particle_system.draw(menu_background)

        events = pygame.event.get()
        menu.update(events)
        menu.draw(screen)

        # Gambar animasi player di tengah
        draw_player_menu_animation(
            screen,
            mode_hover["solo"] or solo_button.is_selected(),
            mode_hover["coop"] or coop_button.is_selected(),
            frame_idx
        )
        frame_idx += 1
        if not (solo_button.is_selected() or coop_button.is_selected()):
            reset_hover()

        pygame.display.flip()
        clock.tick(60)

def player_name_screen():
    menu = create_themed_menu(
        '', 
        WIDTH, 
        HEIGHT
    )
    
    player_name = [""]
    
    def save_name():
        sound_manager.play_ui_click()
        if player_name[0].strip():
            save_game_data(0, 0, player_name[0])
            
            # Show welcome message with animation
            welcome_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            welcome_font = load_font(50)
            welcome_text = welcome_font.render(f"Welcome, {player_name[0]}!", True, (255, 255, 255))
            welcome_rect = welcome_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            
            for alpha in range(0, 255, 5):
                welcome_surface.fill((0, 0, 0, 0))
                welcome_text.set_alpha(alpha)
                welcome_surface.blit(welcome_text, welcome_rect)
                screen.fill((10, 10, 15))
                screen.blit(welcome_surface, (0, 0))
                pygame.display.flip()
                pygame.time.delay(10)
            
            pygame.time.delay(1000)
            
            for alpha in range(255, 0, -5):
                welcome_surface.fill((0, 0, 0, 0))
                welcome_text.set_alpha(alpha)
                welcome_surface.blit(welcome_text, welcome_rect)
                screen.fill((10, 10, 15))
                screen.blit(welcome_surface, (0, 0))
                pygame.display.flip()
                pygame.time.delay(10)
                
            main_menu()
    
    def name_changed(value):
        player_name[0] = value
    
    # Add decorative elements
    menu.add.vertical_margin(150)
    menu.add.label("Begin Your Pixel Adventure", font_size=50, 
                   font_color=(255, 215, 0),
                   font_shadow=True,
                   font_shadow_color=(0, 0, 0),
                   font_shadow_offset=3)
    menu.add.vertical_margin(20)
    menu.add.label("Enter your hero's name:", font_size=30, font_color=(255, 215, 0),
                   font_shadow=True,
                   font_shadow_color=(0, 0, 0),
                   font_shadow_offset=3)
    menu.add.vertical_margin(20)
    
    # Perbaiki masalah dengan cursor_selection_color
    text_input = menu.add.text_input(
        ' ', 
        default='', 
        onchange=name_changed,
        font_size=36,
        selection_color=(255, 255, 150),
        border_width=2,
        border_color=(255, 215, 0),
        # Hapus cursor_selection_color dan gunakan parameter yang didukung
        maxchar=12
    )
    
    menu.add.vertical_margin(30)
    menu.add.button('Begin Journey', save_name, 
                  font_size=40,
                  background_color=(40, 40, 60),
                  border_width=2,
                  border_color=(255, 215, 0))
    
    # Create dynamic background with particles
    while menu.is_enabled():
        particle_system.update()
        
        menu_background.fill((10, 10, 15, 220))
        particle_system.draw(menu_background)
        
        events = pygame.event.get()
        menu.update(events)
        menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
if __name__ == "__main__":
    splash_screen()
    _, _, player_name = load_game_data()
    if not player_name:
        player_name_screen()
    else:
        main_menu()
