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
from ui import HealthBar, MoneyDisplay, XPBar 
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
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    title_font = load_font(72)
    studio_font = load_font(36)
    title_text = title_font.render("Too Many Pixels", True, WHITE)
    studio_text = studio_font.render("D'King Studio", True, WHITE)
    
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    studio_rect = studio_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    
    sound_manager.play_splash_sound()
    
    for alpha in range(255, 0, -5):
        screen.fill(BLACK)
        fade_surface.set_alpha(alpha)
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    pygame.time.delay(2000)
    
    for alpha in range(0, 255, 5):
        screen.fill(BLACK)
        fade_surface.set_alpha(alpha)
        screen.blit(title_text, title_rect)
        screen.blit(studio_text, studio_rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)

def create_blur_surface(surface):
    scale = 0.25
    small_surface = pygame.transform.scale(surface, 
        (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    return pygame.transform.scale(small_surface, 
        (surface.get_width(), surface.get_height()))

def main():
    map_path = os.path.join("assets", "maps", "desert", "plain.png")
    
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
    effects = pygame.sprite.Group()  

    player = Player()
    player.game_map = game_map
    player.sound_manager = sound_manager
    
    partner = Partner(player)
    all_sprites.add(player)
    all_sprites.add(partner)
    
    player.world_bounds = pygame.Rect(
        0,
        0,
        game_map.width,
        game_map.height
    )
    
    player.rect.center = (game_map.width // 2, game_map.height // 2)
    all_sprites.add(player)

    MAX_PROJECTILES = 20
    projectile_pool = []
    for _ in range(MAX_PROJECTILES):
        projectile = Projectile((0,0), (0,0))
        projectile_pool.append(projectile)
        all_sprites.add(projectile)
        projectiles.add(projectile)
        projectile.kill()

    running = True
    paused = False
    enemy_spawn_timer = 0
    projectile_timer = 0
    font = load_font(36)
    health_bar = HealthBar()
    money_display = MoneyDisplay()
    xp_bar = XPBar(WIDTH, HEIGHT)

    death_transition = False
    death_alpha = 0
    blur_surface = None
    FADE_SPEED = 15  
    TRANSITION_DELAY = 5  
    transition_timer = 0
    
    particle_system = ParticleSystem(WIDTH, HEIGHT)
    
    for _ in range(25):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        particle_system.create_particle(x, y)
    
    particle_spawn_timer = 0
    PARTICLE_SPAWN_RATE = 3
    PARTICLES_PER_SPAWN = 2
    
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = True
                pause_menu(screen, main_menu)
                paused = False

        if paused:
            continue

        enemy_spawn_timer += 1
        MAX_ENEMIES = 15
        if enemy_spawn_timer >= 60 and len(enemies) < MAX_ENEMIES:
            enemy = Enemy((player.rect.centerx, player.rect.centery))
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        projectile_timer += 1
        if projectile_timer >= 30 and len(enemies) > 0:
            closest_enemy = None
            min_dist = float('inf')
            
            shoot_radius = 500
            for enemy in enemies:
                dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                              enemy.rect.centery - player.rect.centery)
                if dist < min_dist and dist < shoot_radius:
                    min_dist = dist
                    closest_enemy = enemy

            if closest_enemy:
                for projectile in projectile_pool:
                    if not projectile.alive():
                        start_pos = partner.get_shooting_position()
                        target_pos = (closest_enemy.rect.centerx, closest_enemy.rect.centery)
                        
                        partner.shoot_at(target_pos)
                        
                        projectile.reset(start_pos, target_pos)
                        projectile.add(all_sprites, projectiles)
                        projectile_timer = 0
                        break
            else:
                partner.stop_shooting()

        player.update()
        partner.update(dt)

        for enemy in enemies:
            enemy.update(player)

        projectiles.update()

        experiences.update()
        effects.update(dt)

        hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for projectile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                enemy.take_hit(projectile.damage)
                if enemy.health <= 0:
                    exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(exp)
                    experiences.add(exp)
                    player.session_money += 10

        if not death_transition:
            hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in hits:
                player.health -= 1
                if player.health <= 0:
                    player.start_death_animation()
                    death_transition = True
                    blur_surface = create_blur_surface(screen.copy())
                    break

        if death_transition:
            animation_finished = player.update_death_animation(dt)
            
            screen.blit(blur_surface, (0, 0))
            
            screen.blit(player.image, camera.apply(player))
            
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill((0, 0, 0))
            
            if animation_finished:
                death_alpha = min(death_alpha + FADE_SPEED, 255)
                
                if death_alpha >= 255:
                    transition_timer += 1
                    if transition_timer >= TRANSITION_DELAY:
                        highest_score_menu(screen, player, main_menu, main)
                        return
            
            fade_surface.set_alpha(death_alpha)
            screen.blit(fade_surface, (0, 0))
            
        else:
            hits = pygame.sprite.spritecollide(player, experiences, True)
            for exp in hits:
                player.xp += 5
                player.session_money += 5
                
                if player.xp >= player.max_xp:
                    player.level += 1
                    player.xp -= player.max_xp
                    player.max_xp = int(player.max_xp * 1.2)
                    
                    level_effect = LevelUpEffect(player)
                    effects.add(level_effect)
                    all_sprites.add(level_effect)

            camera.update(player)

            game_map.draw(screen, camera)

            particle_spawn_timer += 1
            if particle_spawn_timer >= PARTICLE_SPAWN_RATE:
                for _ in range(PARTICLES_PER_SPAWN):
                    x = random.randint(0, WIDTH)
                    y = random.randint(0, HEIGHT)
                    particle_system.create_particle(x, y)
                particle_spawn_timer = 0
                
            particle_system.update(camera.x, camera.y)
            
            game_map.draw(screen, camera)
            
            particle_system.draw(screen, camera)
            
            for sprite in all_sprites:
                if isinstance(sprite, Enemy):
                    sprite.draw(screen, (camera.x, camera.y))
                else:
                    screen.blit(sprite.image, camera.apply(sprite))

            health_bar.draw(screen, player.health, player.max_health)
            
            money_display.draw(screen, player.session_money)
            
            xp_bar.draw(screen, player.xp, player.max_xp, player.level)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

def start_game(mode):
    sound_manager.stop_menu_music()
    
    if mode == "solo":
        main()
    elif mode == "split_screen":
        print("Split screen mode is not implemented yet.")

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
                          min(HEIGHT, pygame.display.get_surface().get_height()),
                          theme=theme)
    
    saved_money, highest_score, player_name = load_game_data()
    
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
    
    player_name = [""]
    
    def save_name():
        if player_name[0].strip():
            save_game_data(0, 0, player_name[0])
            main_menu()
    
    def name_changed(value):
        player_name[0] = value
    
    menu.add.label("Please enter your name")
    menu.add.text_input(' ', default='', onchange=name_changed)
    menu.add.button('Confirm', save_name)
    menu.mainloop(screen)

if __name__ == "__main__":
    splash_screen()
    _, _, player_name = load_game_data()
    if not player_name:
        player_name_screen()
    else:
        main_menu()