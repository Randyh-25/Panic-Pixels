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
from utils import pause_menu, highest_score_menu, load_game_data, save_game_data, splitscreen_game_over
from maps import Map
from ui import HealthBar, MoneyDisplay, XPBar, SplitScreenUI
from settings import load_font
from sound_manager import SoundManager
from particles import ParticleSystem
from partner import Partner
from player2 import Player2
from hit_effects import RockHitEffect

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
    map_type = "desert"  # Default to desert map
    
    try:
        game_map = Map(map_path)
    except Exception as e:
        print(f"Error loading map: {e}")
        return

    # Play desert music
    sound_manager.play_gameplay_music(map_type)
    
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
                # Skip enemy yang sedang dalam animasi mati
                if enemy.is_dying:
                    continue
                    
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
            target, damage = enemy.update(player, enemies)
            
            # Jika enemy memberikan damage
            if target and damage > 0:
                player.health -= damage
                if player.health <= 0:
                    player.start_death_animation()
                    death_transition = True
                    blur_surface = create_blur_surface(screen.copy())
                    break

        projectiles.update()

        experiences.update()
        effects.update(dt)

        hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for projectile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                # Skip enemy yang sudah dalam animasi mati
                if enemy.is_dying:
                    continue
                
                # Tambahkan efek hit dari rock
                hit_effect = RockHitEffect((enemy.rect.centerx, enemy.rect.centery))
                all_sprites.add(hit_effect)
                effects.add(hit_effect)
                
                enemy.take_hit(projectile.damage)
                if enemy.health <= 0:
                    exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(exp)
                    experiences.add(exp)
                    player.session_money += 10

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
                        # Stop the gameplay music before going to score menu
                        sound_manager.stop_gameplay_music()
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
                    
                    # Tambahkan max health saat level up
                    player.max_health += 20
                    player.health = player.max_health  # Isi penuh health
                    
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
        split_screen_main()

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
    menu.add.button('Co-op Multiplayer', lambda: start_game("split_screen"))
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

def split_screen_main():
    map_path = os.path.join("assets", "maps", "desert", "plain.png")
    map_type = "desert"  # Default to desert map
    
    try:
        game_map = Map(map_path)
    except Exception as e:
        print(f"Error loading map: {e}")
        return

    # Play desert music
    sound_manager.play_gameplay_music(map_type)
    
    camera = Camera(game_map.width, game_map.height)

    # Define the draw_game function first
    def draw_game(viewport, offset_x=0, player_filter=None):
        viewport_surface = screen.subsurface(viewport)
        
        # Tentukan kamera yang tepat berdasarkan viewport
        cam_x = camera.x
        cam_y = camera.y
        
        # Jika kita menggambar viewport kanan, gunakan x2/y2
        if camera.split_mode and offset_x > 0:
            cam_x = camera.x2
            cam_y = camera.y2
        
        # Gambar map dan particles
        game_map.draw(viewport_surface, (cam_x, cam_y))
        particle_system.draw(viewport_surface, (cam_x, cam_y))
        
        # Viewport rect untuk deteksi batas layar
        world_view_rect = pygame.Rect(-cam_x, -cam_y, viewport.width, viewport.height)
        
        # Gambar semua sprite dengan kondisi filter
        for sprite in all_sprites:
            # Jika dalam mode split screen, filter berdasarkan viewport
            if camera.split_mode:
                # Kasus khusus untuk player dan partner
                if hasattr(sprite, 'player_id'):
                    # Di viewport kiri hanya gambar player1 dan partner1
                    if offset_x == 0 and sprite.player_id == 2:
                        continue
                    # Di viewport kanan hanya gambar player2 dan partner2
                    if offset_x > 0 and sprite.player_id == 1:
                        continue
            
            # Hanya gambar sprite jika ada dalam viewport
            if world_view_rect.colliderect(sprite.rect):
                if isinstance(sprite, Enemy):
                    sprite.draw(viewport_surface, (cam_x, cam_y))
                else:
                    # Untuk viewport kanan, kita perlu menyesuaikan posisi x kamera
                    if camera.split_mode and offset_x > 0:
                        # Berikan offset tambahan untuk kompensasi viewport kanan
                        pos_x = sprite.rect.x + cam_x
                        pos_y = sprite.rect.y + cam_y
                        viewport_surface.blit(sprite.image, (pos_x, pos_y))
                    else:
                        viewport_surface.blit(sprite.image, (sprite.rect.x + cam_x, sprite.rect.y + cam_y))

    # Continue with the rest of split_screen_main function
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles1 = pygame.sprite.Group()
    projectiles2 = pygame.sprite.Group()
    experiences = pygame.sprite.Group()
    effects = pygame.sprite.Group()

    # Initialize both players and their partners
    player1 = Player()
    player2 = Player2()
    
    for player in [player1, player2]:
        player.game_map = game_map
        player.sound_manager = sound_manager
        player.world_bounds = pygame.Rect(0, 0, game_map.width, game_map.height)
    
    # Position players apart from each other
    player1.rect.center = (game_map.width // 2 - 100, game_map.height // 2)
    player2.rect.center = (game_map.width // 2 + 100, game_map.height // 2)
    
    partner1 = Partner(player1)
    partner2 = Partner(player2)
    
    all_sprites.add(player1, player2, partner1, partner2)

    # Set player_id for partners
    partner1.player_id = 1
    partner2.player_id = 2

    # Create projectile pools for both players
    MAX_PROJECTILES = 20
    projectile_pool1 = []
    projectile_pool2 = []
    
    for _ in range(MAX_PROJECTILES):
        for pool, group in [(projectile_pool1, projectiles1), (projectile_pool2, projectiles2)]:
            projectile = Projectile((0,0), (0,0))
            pool.append(projectile)
            all_sprites.add(projectile)
            group.add(projectile)
            projectile.kill()

    running = True
    paused = False
    enemy_spawn_timer = 0
    projectile_timer = 0
    
    # Initialize split screen UI
    ui = SplitScreenUI(WIDTH, HEIGHT)
    
    death_transition = False
    death_alpha = 0
    blur_surface = None
    FADE_SPEED = 15
    TRANSITION_DELAY = 5
    transition_timer = 0
    
    particle_system = ParticleSystem(WIDTH, HEIGHT)
    
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

        # Spawn enemies
        enemy_spawn_timer += 1
        MAX_ENEMIES = 20  # Increased for 2 players
        if enemy_spawn_timer >= 60 and len(enemies) < MAX_ENEMIES:
            # Spawn near random player
            target_player = random.choice([player1, player2])
            enemy = Enemy((target_player.rect.centerx, target_player.rect.centery))
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        # Handle projectiles for both players
        projectile_timer += 1
        if projectile_timer >= 30 and len(enemies) > 0:
            for player, partner, pool, projs in [
                (player1, partner1, projectile_pool1, projectiles1),
                (player2, partner2, projectile_pool2, projectiles2)
            ]:
                closest_enemy = None
                min_dist = float('inf')
                shoot_radius = 500
                
                for enemy in enemies:
                    # Skip enemy yang sedang dalam animasi mati
                    if enemy.is_dying:
                        continue
                        
                    dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                                  enemy.rect.centery - player.rect.centery)
                    if dist < min_dist and dist < shoot_radius:
                        min_dist = dist
                        closest_enemy = enemy

                if closest_enemy:
                    for projectile in pool:
                        if not projectile.alive():
                            start_pos = partner.get_shooting_position()
                            target_pos = (closest_enemy.rect.centerx, closest_enemy.rect.centery)
                            partner.shoot_at(target_pos)
                            projectile.reset(start_pos, target_pos)
                            projectile.add(all_sprites, projs)
                            projectile_timer = 0
                            break
                else:
                    partner.stop_shooting()

        # Update all game objects
        player1.update()
        player2.update()
        partner1.update(dt)
        partner2.update(dt)
        
        for enemy in enemies:
            # Enemies target the nearest LIVING player
            p1_dist = float('inf') if player1.is_dying else math.hypot(
                         player1.rect.centerx - enemy.rect.centerx,
                         player1.rect.centery - enemy.rect.centery)
            p2_dist = float('inf') if player2.is_dying else math.hypot(
                         player2.rect.centerx - enemy.rect.centerx,
                         player2.rect.centery - enemy.rect.centery)
                 
            # Pilih pemain yang masih hidup
            if p1_dist == float('inf') and p2_dist == float('inf'):
                # Jika keduanya mati, target acak (ini jarang terjadi)
                target = random.choice([player1, player2])
            else:
                target = player1 if p1_dist < p2_dist else player2
                
            hit_target, damage = enemy.update(target, enemies)
            
            # Jika enemy memberikan damage
            if hit_target and damage > 0:
                hit_target.health -= damage
                if hit_target.health <= 0:
                    hit_target.start_death_animation()
                    if not death_transition:  # Ambil screenshot blur hanya sekali
                        death_transition = True
                        blur_surface = create_blur_surface(screen.copy())
                    break

        projectiles1.update()
        projectiles2.update()
        experiences.update()
        effects.update(dt)

        # Handle projectile hits
        for projs in [projectiles1, projectiles2]:
            hits = pygame.sprite.groupcollide(projs, enemies, True, False)
            for projectile, hit_enemies in hits.items():
                for enemy in hit_enemies:
                    # Skip enemy yang sudah dalam animasi mati
                    if enemy.is_dying:
                        continue
                        
                    # Tambahkan efek hit dari rock
                    hit_effect = RockHitEffect((enemy.rect.centerx, enemy.rect.centery))
                    all_sprites.add(hit_effect)
                    effects.add(hit_effect)
                    
                    enemy.take_hit(projectile.damage)
                    if enemy.health <= 0:
                        exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                        all_sprites.add(exp)
                        experiences.add(exp)
                        # Split money between players
                        player1.session_money += 5
                        player2.session_money += 5

        # Handle death transition
        if death_transition:
            if player1.health <= 0:
                player1.update_death_animation(dt)
            if player2.health <= 0:
                player2.update_death_animation(dt)
                
            both_dead = player1.health <= 0 and player2.health <= 0
            if both_dead:
                death_alpha = min(death_alpha + FADE_SPEED, 255)
                fade_surface = pygame.Surface((WIDTH, HEIGHT))
                fade_surface.fill(BLACK)
                fade_surface.set_alpha(death_alpha)
                screen.blit(fade_surface, (0, 0))
                
                if death_alpha >= 255:
                    transition_timer += 1
                    if transition_timer >= TRANSITION_DELAY:
                        # Stop the gameplay music before going to game over screen
                        sound_manager.stop_gameplay_music()
                        splitscreen_game_over(screen, player1, player2, main_menu, split_screen_main)
                        return

        # Handle experience collection
        for player in [player1, player2]:
            hits = pygame.sprite.spritecollide(player, experiences, True)
            for exp in hits:
                player.xp += 5
                player.session_money += 5
                
                if player.xp >= player.max_xp:
                    player.level += 1
                    player.xp -= player.max_xp
                    player.max_xp = int(player.max_xp * 1.2)
                    
                    # Tambahkan max health saat level up
                    player.max_health += 20
                    player.health = player.max_health  # Isi penuh health
                    
                    level_effect = LevelUpEffect(player)
                    effects.add(level_effect)
                    all_sprites.add(level_effect)

        # Update camera to follow midpoint between players
        if player1.health <= 0:
            # Player 1 mati, kamera ikuti player 2
            camera.update(player2)
        elif player2.health <= 0:
            # Player 2 mati, kamera ikuti player 1
            camera.update(player1)
        else:
            # Kedua player hidup, gunakan kamera split screen
            camera.update(player1, player2)

        # Draw everything
        if camera.split_mode:
            # Draw more visible divider between viewports
            divider_width = 4  # Lebar garis pemisah (4 pixel)
            divider_rect = pygame.Rect(WIDTH//2 - divider_width//2, 0, divider_width, HEIGHT)
            pygame.draw.rect(screen, (255, 215, 0), divider_rect)  # Warna kuning emas untuk visibilitas
            
            # Optional: Tambahkan shadow effect untuk kedalaman
            shadow_width = 2
            pygame.draw.rect(screen, (100, 100, 100, 128), 
                            pygame.Rect(WIDTH//2 - divider_width//2 - shadow_width, 0, shadow_width, HEIGHT))
            pygame.draw.rect(screen, (100, 100, 100, 128), 
                            pygame.Rect(WIDTH//2 + divider_width//2, 0, shadow_width, HEIGHT))
            
            # Draw left viewport (Player 1)
            left_viewport = pygame.Rect(0, 0, WIDTH//2 - divider_width//2, HEIGHT)
            draw_game(left_viewport, 0, 1)  # Draw with player 1 filter
            
            # Draw right viewport (Player 2)
            right_viewport = pygame.Rect(WIDTH//2 + divider_width//2, 0, WIDTH//2 - divider_width//2, HEIGHT)
            draw_game(right_viewport, WIDTH//2, 2)  # Draw with player 2 filter
            
            # Draw UI for both players
            ui.draw_split(screen, player1, player2, True)
        else:
            # Normal single screen drawing
            full_viewport = pygame.Rect(0, 0, WIDTH, HEIGHT)
            draw_game(full_viewport)
            ui.draw(screen, player1, player2)

        pygame.display.flip()

    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    splash_screen()
    _, _, player_name = load_game_data()
    if not player_name:
        player_name_screen()
    else:
        main_menu()