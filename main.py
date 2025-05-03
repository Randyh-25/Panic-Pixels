# main.py
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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  # Start in fullscreen mode
pygame.display.set_caption("Survivor Game")
clock = pygame.time.Clock()

def main():
    # Muat peta latar belakang
    game_map = Map("assets/maps/debugmap.png")

    # Inisialisasi kamera
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
            enemy = Enemy()
            enemy.rect.x = player.rect.x + random.randint(-300, 300)
            enemy.rect.y = player.rect.y + random.randint(-300, 300)
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        projectile_timer += 1
        if projectile_timer >= 30:
            closest_enemy = None
            min_dist = float('inf')
            for enemy in enemies:
                # Hitung jarak antara pemain dan musuh
                dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                                  enemy.rect.centery - player.rect.centery)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy

            # Jika ada musuh terdekat, tembak proyektil
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

        # Tampilkan teks kesehatan dan skor
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def start_game(mode):
    if mode == "solo":
        main()  # Start the main game loop
    elif mode == "split_screen":
        print("Split screen mode is not implemented yet.")  # Placeholder

def settings_menu():
    menu = pygame_menu.Menu('Settings', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    resolutions = [('800x600', (800, 600)), ('1024x768', (1024, 768)), ('1280x720', (1280, 720))]
    menu.add.selector('Resolution: ', resolutions, onchange=lambda _, res: pygame.display.set_mode(res))
    menu.add.toggle_switch('Fullscreen: ', False, onchange=lambda value: pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if value else 0))
    menu.add.range_slider('Master Volume: ', default=50, range_values=(0, 100), increment=1, onchange=lambda value: print(f"Volume set to {value}"))
    menu.add.button('Back', main_menu)
    menu.mainloop(screen)

def quit_confirmation():
    menu = pygame_menu.Menu('Quit Confirmation', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.label('Are you sure you want to quit?')
    menu.add.button('Yes', pygame.quit)
    menu.add.button('No', main_menu)
    menu.mainloop(screen)

from settings import settings_menu

def main_menu():
    menu = pygame_menu.Menu('Main Menu', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_DARK)
    menu.add.button('Start', lambda: game_mode_menu())
    menu.add.button('Settings', lambda: settings_menu(screen, main_menu))
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
