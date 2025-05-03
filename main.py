# main.py
import pygame
import sys
import math
from settings import *
from player import Player
from enemy import Enemy
from projectile import Projectile
from experience import Experience

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survivor Game")
clock = pygame.time.Clock()

def main():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    experiences = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    running = True
    enemy_spawn_timer = 0
    projectile_timer = 0
    font = pygame.font.SysFont(None, 36)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        enemy_spawn_timer += 1
        if enemy_spawn_timer >= 60:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy_spawn_timer = 0

        projectile_timer += 1
        if projectile_timer >= 30:
            closest_enemy = None
            min_dist = float('inf')
            for enemy in enemies:
                dist = math.hypot(enemy.rect.centerx - player.rect.centerx,
                                  enemy.rect.centery - player.rect.centery)
                if dist < min_dist:
                    min_dist = dist
                    closest_enemy = enemy
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

        # Collisions
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

        hits = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in hits:
            player.health -= 1
            if player.health <= 0:
                running = False

        hits = pygame.sprite.spritecollide(player, experiences, True)
        for exp in hits:
            player.score += 5

        screen.fill(BLACK)
        all_sprites.draw(screen)
        health_text = font.render(f"Health: {player.health}", True, WHITE)
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 50))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
