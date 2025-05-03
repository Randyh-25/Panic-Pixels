import pygame
import random
import sys
import math
from settings import *
from player import Player, Camera
from enemy import Enemy
from projectile import Projectile
from experience import Experience
import pygame_menu
from utils import pause_menu, highest_score_menu
from maps import Map
from ui import HealthBar  

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  
pygame.display.set_caption("Pixel Panic")
clock = pygame.time.Clock()

def main():
    game_map = Map("assets/maps/debugmap.png")
    camera = Camera(game_map.width, game_map.height)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    experiences = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    running = True
    paused = False
    enemy_spawn_timer = 0
    projectile_timer = 0
    font = pygame.font.SysFont(None, 36)
    health_bar = HealthBar()

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                paused = True
                pause_menu(screen, main_menu)  # Show pause menu
                paused = False

        if paused:
            continue

        # Update logika permainan
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60:
            # Spawn musuh di sekitar pemain
            enemy = Enemy((player.rect.centerx, player.rect.centery))
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        projectile_timer += 1
        if projectile_timer >= 30 and len(enemies) > 0:  # Pastikan ada musuh
            closest_enemy = None
            min_dist = float('inf')
            
            # Cari musuh terdekat tanpa batasan jarak
            for enemy in enemies:
                dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                              enemy.rect.centery - player.rect.centery)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy

            # Selalu tembak jika ada musuh
            if closest_enemy:
                projectile = Projectile(player.rect.centerx, player.rect.centery,
                                    closest_enemy.rect.centerx, closest_enemy.rect.centery)
                all_sprites.add(projectile)
                projectiles.add(projectile)
                projectile_timer = 0

        player.update()

        for enemy in enemies:
            enemy.update(player)

        projectiles.update()

        # Deteksi tabrakan antara proyektil dan musuh
        hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for projectile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                enemy.health -= projectile.damage
                if enemy.health <= 0:
                    exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(exp)
                    experiences.add(exp)
                    enemy.kill()
                    player.score += 10

        # Deteksi tabrakan antara pemain dan musuh
        hits = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in hits:
            player.health -= 1
            if player.health <= 0:
                highest_score_menu(screen, player.score, main_menu, main)
                return

        # Deteksi tabrakan antara pemain dan experience
        hits = pygame.sprite.spritecollide(player, experiences, True)  # True untuk menghapus experience
        for exp in hits:
            player.score += 5  # Tambahkan skor pemain

        # Update kamera
        camera.update(player)

        # Tampilkan latar belakang
        game_map.draw(screen, camera)

        # Gambar semua sprite dengan kamera
        for sprite in all_sprites:
            screen.blit(sprite.image, camera.apply(sprite))

        # Ganti bagian render health text dengan health bar
        # Hapus atau comment baris ini:
        # health_text = font.render(f"Health: {player.health}", True, WHITE)
        # screen.blit(health_text, (10, 10))
        
        # Tambahkan render health bar
        health_bar.draw(screen, player.health, player.max_health)
        
        # Tetap tampilkan score
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 40))  # Sesuaikan posisi y agar tidak tumpang tindih
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

def start_game(mode):
    if mode == "solo":
        main()  # Start the main game loop
    elif mode == "split_screen":
        print("Split screen mode is not implemented yet.")  # Placeholder

def settings_menu():
    menu = pygame_menu.Menu('Settings', min(WIDTH, pygame.display.get_surface().get_width()),
                          min(HEIGHT, pygame.display.get_surface().get_height()),
                          theme=pygame_menu.themes.THEME_DARK)
    
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

    resolution_selector = menu.add.selector('Resolution: ', RESOLUTIONS, onchange=change_resolution)
    if FULLSCREEN:
        resolution_selector.hide()
    
    menu.add.toggle_switch('Fullscreen: ', FULLSCREEN, onchange=toggle_fullscreen)
    menu.add.range_slider('Master Volume: ', default=VOLUME, range_values=(0, 100), 
                         increment=1, onchange=lambda value: setattr(sys.modules[__name__], 'VOLUME', value))
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def quit_confirmation():
    menu = pygame_menu.Menu('Quit Confirmation', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.label('Are you sure you want to quit?')
    menu.add.button('Yes', pygame.quit)
    menu.add.button('No', main_menu)
    menu.mainloop(screen)

def main_menu():
    menu = pygame_menu.Menu('Main Menu', 
                          min(WIDTH, pygame.display.get_surface().get_width()),
                          min(HEIGHT, pygame.display.get_surface().get_height()),
                          theme=pygame_menu.themes.THEME_DARK)
    menu.add.button('Start', game_mode_menu)
    menu.add.button('Settings', settings_menu)
    menu.add.button('Quit', quit_confirmation)
    menu.mainloop(screen)

def game_mode_menu():
    menu = pygame_menu.Menu('Game Mode', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.button('Solo', lambda: start_game("solo"))
    menu.add.button('Split Screen', lambda: start_game("split_screen"))
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

if __name__ == "__main__":
    main_menu()
