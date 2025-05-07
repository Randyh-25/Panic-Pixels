import pygame
import random
import sys
import math
import os
from settings import *
from player import Player, Camera
from enemy import Enemy
from projectile import Projectile
from experience import Experience, LevelUpEffect
import pygame_menu
from utils import pause_menu, highest_score_menu, load_game_data, save_game_data
from maps import Map
from ui import HealthBar  
from ui import MoneyDisplay  
from ui import XPBar 
from settings import load_font
from sound_manager import SoundManager
from particles import ParticleSystem
from partner import Partner

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  
pygame.display.set_caption("Too Many Pixels")
clock = pygame.time.Clock()
sound_manager = SoundManager()

def splash_screen():
    # Create a surface for fading
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    # Create text for logo
    title_font = load_font(72)
    studio_font = load_font(36)
    title_text = title_font.render("Too Many Pixels", True, WHITE)
    studio_text = studio_font.render("D'King Studio", True, WHITE)
    
    # Position text in center
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    studio_rect = studio_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    
    # Play splash sound at the start
    sound_manager.play_splash_sound()
    
    # Fade in
    for alpha in range(255, 0, -5):  # 255 to 0 for fade in
        screen.fill(BLACK)
        fade_surface.set_alpha(alpha)
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Hold the screen
    pygame.time.delay(2000)  # Show splash for 2 seconds
    
    # Fade out
    for alpha in range(0, 255, 5):  # 0 to 255 for fade out
        screen.fill(BLACK)
        fade_surface.set_alpha(alpha)
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)

def create_blur_surface(surface):
    # Create a simple blur effect
    scale = 0.25
    small_surface = pygame.transform.scale(surface, 
        (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    return pygame.transform.scale(small_surface, 
        (surface.get_width(), surface.get_height()))

def main():
    # Update map path to be more explicit
    map_path = os.path.join("assets", "maps", "desert", "plain.png")
    
    # Add error handling for map loading
    try:
        game_map = Map(map_path)
    except Exception as e:
        print(f"Error loading map: {e}")
        return

    camera = Camera(game_map.width, game_map.height)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    experiences = pygame.sprite.Group()
    effects = pygame.sprite.Group()  # Tambahkan sprite group untuk effects

    # Create player only once
    player = Player()
    player.game_map = game_map  # Add map reference to player
    player.sound_manager = sound_manager  # Add sound manager reference
    
    # Create partner and add to sprites
    partner = Partner(player)
    all_sprites.add(player)
    all_sprites.add(partner)
    
    # Set world bounds for the expanded map
    player.world_bounds = pygame.Rect(
        0,                  # Left boundary
        0,                  # Top boundary
        game_map.width,     # Right boundary (4x original width)
        game_map.height     # Bottom boundary (4x original height)
    )
    
    # Position player at center of expanded map
    player.rect.center = (game_map.width // 2, game_map.height // 2)
    all_sprites.add(player)

    # Object pooling untuk projectiles
    MAX_PROJECTILES = 20
    projectile_pool = []
    for _ in range(MAX_PROJECTILES):
        projectile = Projectile((0,0), (0,0))
        projectile_pool.append(projectile)
        all_sprites.add(projectile)
        projectiles.add(projectile)
        projectile.kill()  # Deactivate initially

    running = True
    paused = False
    enemy_spawn_timer = 0
    projectile_timer = 0
    font = load_font(36)  # Replace SysFont with custom font
    health_bar = HealthBar()
    money_display = MoneyDisplay()  # Tambahkan money display
    xp_bar = XPBar(WIDTH, HEIGHT)  # Add XP bar

    # Modify death transition variables
    death_transition = False
    death_alpha = 0
    blur_surface = None
    FADE_SPEED = 15  
    TRANSITION_DELAY = 5  
    transition_timer = 0
    
    # Create particle system with more initial particles
    particle_system = ParticleSystem(WIDTH, HEIGHT)
    
    # Kurangi jumlah partikel awal
    for _ in range(25):  # Kurangi dari 50 menjadi 25
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        particle_system.create_particle(x, y)
    
    # Particle spawn settings
    particle_spawn_timer = 0
    PARTICLE_SPAWN_RATE = 3  # Tingkatkan dari 1 ke 3 (lebih jarang spawn)
    PARTICLES_PER_SPAWN = 2  # Kurangi dari 5 ke 2
    
    while running:
        dt = clock.tick(FPS) / 1000.0  # Convert to seconds

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = True
                pause_menu(screen, main_menu)  # Show pause menu
                paused = False

        if paused:
            continue

        # Update logika permainan
        enemy_spawn_timer += 1
        MAX_ENEMIES = 15  # Batasi jumlah maksimum musuh
        if enemy_spawn_timer >= 60 and len(enemies) < MAX_ENEMIES:
            enemy = Enemy((player.rect.centerx, player.rect.centery))
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        projectile_timer += 1
        if projectile_timer >= 30 and len(enemies) > 0:  # Pastikan ada musuh
            closest_enemy = None
            min_dist = float('inf')
            
            # Cari musuh terdekat dalam radius tertentu
            shoot_radius = 500  # Radius tembak dalam pixel
            for enemy in enemies:
                dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                              enemy.rect.centery - player.rect.centery)
                if dist < min_dist and dist < shoot_radius:
                    min_dist = dist
                    closest_enemy = enemy

            # Gunakan projectile dari pool
            if closest_enemy:
                # Cari projectile yang tidak aktif
                for projectile in projectile_pool:
                    if not projectile.alive():
                        start_pos = partner.get_shooting_position()
                        target_pos = (closest_enemy.rect.centerx, closest_enemy.rect.centery)
                        projectile.reset(start_pos, target_pos)  # Reset posisi dan aktifkan
                        projectile.add(all_sprites, projectiles)
                        projectile_timer = 0
                        break

        player.update()
        partner.update(dt)

        for enemy in enemies:
            enemy.update(player)

        projectiles.update()

        # Tambahkan update untuk experiences
        experiences.update()
        effects.update(dt)  # Tambahkan update untuk effects

        # Deteksi tabrakan antara proyektil dan musuh
        hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for projectile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                enemy.health -= projectile.damage
                if enemy.health <= 0:
                    # Start death animation instead of immediately killing
                    enemy.start_death_animation()
                    # Create experience object
                    exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(exp)
                    experiences.add(exp)
                    player.session_money += 10

        # Deteksi tabrakan antara pemain dan musuh
        if not death_transition:
            hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in hits:
                player.health -= 1
                if player.health <= 0:
                    player.start_death_animation()
                    death_transition = True
                    # Create blur surface from current game state
                    blur_surface = create_blur_surface(screen.copy())
                    break

        if death_transition:
            # Update death animation
            animation_finished = player.update_death_animation(dt)
            
            # Draw game state with blur
            screen.blit(blur_surface, (0, 0))
            
            # Draw player death animation
            screen.blit(player.image, camera.apply(player))
            
            # Create fade overlay
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill((0, 0, 0))
            
            if animation_finished:
                # Faster fade out
                death_alpha = min(death_alpha + FADE_SPEED, 255)
                
                if death_alpha >= 255:
                    transition_timer += 1
                    if transition_timer >= TRANSITION_DELAY:
                        # Transition to score menu
                        highest_score_menu(screen, player, main_menu, main)
                        return
            
            fade_surface.set_alpha(death_alpha)
            screen.blit(fade_surface, (0, 0))
            
        else:
            # Deteksi tabrakan antara pemain dan experience
            hits = pygame.sprite.spritecollide(player, experiences, True)
            for exp in hits:
                player.xp += 5
                player.session_money += 5  # Money from collecting experience
                
                # Level up check
                if player.xp >= player.max_xp:
                    player.level += 1
                    player.xp -= player.max_xp
                    player.max_xp = int(player.max_xp * 1.2)  # Increase XP needed for next level
                    
                    # Create level up effect
                    level_effect = LevelUpEffect(player)
                    effects.add(level_effect)
                    all_sprites.add(level_effect)

            # Update kamera
            camera.update(player)

            # Tampilkan latar belakang
            game_map.draw(screen, camera)

            # Update particle system
            particle_spawn_timer += 1
            if particle_spawn_timer >= PARTICLE_SPAWN_RATE:
                # Spawn new particles across the screen
                for _ in range(PARTICLES_PER_SPAWN):
                    x = random.randint(0, WIDTH)
                    y = random.randint(0, HEIGHT)
                    particle_system.create_particle(x, y)
                particle_spawn_timer = 0
                
            particle_system.update(camera.x, camera.y)
            
            # Draw game elements in order
            game_map.draw(screen, camera)
            
            # Draw particles before sprites but after map
            particle_system.draw(screen, camera)
            
            # Draw sprites
            for sprite in all_sprites:
                screen.blit(sprite.image, camera.apply(sprite))

            # Tambahkan render health bar
            health_bar.draw(screen, player.health, player.max_health)
            
            # Tambahkan tampilan money
            money_display.draw(screen, player.session_money)
            
            # Draw XP bar last so it's always on top
            xp_bar.draw(screen, player.xp, player.max_xp, player.level)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

def start_game(mode):
    # Stop menu music before starting game
    sound_manager.stop_menu_music()
    
    if mode == "solo":
        main()  # Start the main game loop
    elif mode == "split_screen":
        print("Split screen mode is not implemented yet.")  # Placeholder

def settings_menu():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Settings', min(WIDTH, pygame.display.get_surface().get_width()),
                          min(HEIGHT, pygame.display.get_surface().get_height()),
                          theme=theme)
    
    def toggle_fullscreen(value):
        global FULLSCREEN
        FULLSCREEN = value
        if value:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            resolution_selector.hide()
        else:
            pygame.display.set_mode(CURRENT_RESOLUTION)
            resolution_selector.show()

    def change_resolution(_, res):
        global CURRENT_RESOLUTION
        if not FULLSCREEN:
            CURRENT_RESOLUTION = res
            pygame.display.set_mode(res)
            # Update menu size setelah mengubah resolusi
            menu.resize(min(res[0], pygame.display.get_surface().get_width()),
                       min(res[1], pygame.display.get_surface().get_height()))

    def change_volume(value):
        global VOLUME
        VOLUME = value
        sound_manager.set_volume(value)

    resolution_selector = menu.add.selector('Resolution: ', RESOLUTIONS, onchange=change_resolution)
    if FULLSCREEN:
        resolution_selector.hide()
    
    menu.add.toggle_switch('Fullscreen: ', FULLSCREEN, onchange=toggle_fullscreen)
    menu.add.range_slider('Master Volume: ', default=VOLUME, range_values=(0, 100), 
                         increment=1, onchange=change_volume)
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def quit_confirmation():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Quit Confirmation', WIDTH, HEIGHT, theme=theme)
    menu.add.label('Are you sure you want to quit?')
    menu.add.button('Yes', pygame.quit)
    menu.add.button('No', main_menu)
    menu.mainloop(screen)

def main_menu():
    sound_manager.play_menu_music()
    
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Main Menu', 
                          min(WIDTH, pygame.display.get_surface().get_width()),
                          min(HEIGHT, pygame.display.get_surface().get_height()),  # Fixed get_height method
                          theme=theme)
    
    # Load player data
    saved_money, highest_score, player_name = load_game_data()
    
    # Add player info
    if player_name:
        menu.add.label(f"Welcome, {player_name}!")
        menu.add.label(f"Total Money: {saved_money}")
    
    menu.add.button('Start', game_mode_menu)
    menu.add.button('Settings', settings_menu)
    menu.add.button('Quit', quit_confirmation)
    menu.mainloop(screen)

def game_mode_menu():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu('Game Mode', WIDTH, HEIGHT, theme=theme)
    menu.add.button('Solo', lambda: start_game("solo"))
    menu.add.button('Split Screen', lambda: start_game("split_screen"))
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def player_name_screen():
    theme = pygame_menu.themes.THEME_DARK.copy()
    theme.widget_font = FONT_PATH
    theme.title_font = FONT_PATH
    
    menu = pygame_menu.Menu(
        'Welcome to "Too Many Pixels"', 
        WIDTH, 
        HEIGHT,
        theme=theme
    )
    
    player_name = [""]  # Use list to store name for reference in callback
    
    def save_name():
        if player_name[0].strip():  # Check if name isn't empty
            save_game_data(0, 0, player_name[0])  # Save initial data with player name
            main_menu()  # Proceed to main menu
    
    def name_changed(value):
        player_name[0] = value
    
    menu.add.label("Please enter your name")
    menu.add.text_input(' ', default='', onchange=name_changed)
    menu.add.button('Confirm', save_name)
    menu.mainloop(screen)

if __name__ == "__main__":
    splash_screen()
    # Check if save file exists
    _, _, player_name = load_game_data()
    if not player_name:
        player_name_screen()
    else:
        main_menu()
