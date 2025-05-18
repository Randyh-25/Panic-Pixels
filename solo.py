import pygame
import random
import math
import os
from settings import *
from player import Player, Camera
from enemy import Enemy
from projectile import Projectile
from experience import Experience, LevelUpEffect
from utils import pause_menu, highest_score_menu, load_game_data, save_game_data
from maps import Map
from ui import HealthBar, MoneyDisplay, XPBar, InteractionButton, render_text_with_border
from settings import load_font
from particles import ParticleSystem
from partner import Partner
from hit_effects import RockHitEffect
from devil import Devil

def create_blur_surface(surface):
    scale = 0.25
    small_surface = pygame.transform.scale(surface, 
        (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    return pygame.transform.scale(small_surface, 
        (surface.get_width(), surface.get_height()))

def main(screen, clock, sound_manager, main_menu_callback):
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
    
    session_start_ticks = pygame.time.get_ticks()  # Simpan waktu mulai session
    pause_ticks = 0
    pause_start = None

    cheat_pause_ticks = 0      
    cheat_pause_start = None   

    cheat_mode = False
    cheat_input = ""
    cheat_message = ""
    original_max_health = None
    original_health = None

    devil = None
    devil_spawn_times = [4*60*1000]  # ms, menit ke-4
    next_devil_time = devil_spawn_times[0]
    devil_notif_timer = 0
    devil_notif_show = False

    # Add interaction button and shop
    interaction_button = InteractionButton()
    from ui import DevilShop
    devil_shop = DevilShop()
    
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Collect events before processing to pass to shop
        current_events = []
        for event in pygame.event.get():
            current_events.append(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if devil_shop.is_open:
                        devil_shop.close()
                    else:
                        paused = True
                        pause_start = pygame.time.get_ticks()  # MULAI PAUSE
                        pause_menu(screen, main_menu_callback)
                        paused = False
                        if pause_start is not None:
                            pause_ticks += pygame.time.get_ticks() - pause_start  # TAMBAHKAN DURASI PAUSE
                            pause_start = None
                # Add cheat console toggle
                elif event.key == pygame.K_BACKQUOTE:
                    cheat_mode = not cheat_mode
                    if cheat_mode:
                        cheat_pause_start = pygame.time.get_ticks()
                    else:
                        if cheat_pause_start is not None:
                            cheat_pause_ticks += pygame.time.get_ticks() - cheat_pause_start
                            cheat_pause_start = None
                    cheat_input = ""
                    cheat_message = ""
                # Add E key to open shop when interaction is possible
                elif event.key == pygame.K_e:
                    if devil and devil.can_interact():
                        devil_shop.open()

        if devil_shop.is_open:
            devil_shop.update(current_events)
            # Skip regular game updates while shop is open
            devil_shop.draw(screen)
            pygame.display.flip()
            continue

        if paused:
            continue

        # Cheat input handling
        if cheat_mode:
            # Draw semi-transparent overlay (benar-benar transparan, game tetap terlihat)
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 80))  # alpha 80, makin kecil makin transparan
            screen.blit(overlay, (0, 0))

            # Draw input box
            font_cheat = load_font(36)
            box_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 40, 400, 80)
            pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=8)
            pygame.draw.rect(screen, (200, 200, 200), box_rect, 2, border_radius=8)

            input_surface = font_cheat.render(cheat_input, True, (255, 255, 0))
            screen.blit(input_surface, (box_rect.x + 20, box_rect.y + 20))

            # Draw message if any, geser ke bawah kotak
            if cheat_message:
                msg_surface = font_cheat.render(cheat_message, True, (0, 255, 0))
                msg_rect = msg_surface.get_rect(center=(WIDTH//2, box_rect.y + box_rect.height + 30))
                screen.blit(msg_surface, msg_rect)

            pygame.display.flip()

            # Handle text input for cheat console
            keys = pygame.key.get_pressed()
            for event in current_events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # Process cheat command
                        if cheat_input == "orkaybanh":
                            player.session_money += 10000
                            cheat_message = "Money +10000!"
                        elif cheat_input == "armordaribapak":
                            if original_max_health is None:
                                original_max_health = player.max_health
                                original_health = player.health
                            player.max_health = 1000
                            player.health = 1000
                            cheat_message = "Armor dari bapak aktif!"
                        elif cheat_input == "rakyatbiasa":
                            if original_max_health is not None:
                                player.max_health = original_max_health
                                player.health = original_health
                                original_max_health = None
                                original_health = None
                            cheat_message = "Cheat dinonaktifkan!"
                        elif cheat_input == "timeheist":
                            session_start_ticks -= 230 * 1000
                            cheat_message = "Waktu dipercepat +3:50!"
                        elif cheat_input == "dealwiththedevil":
                            if devil is None:
                                devil = Devil(game_map.width, game_map.height)
                                all_sprites.add(devil)
                                cheat_message = "Devil muncul!"
                            else:
                                cheat_message = "Devil sudah ada!"
                        else:
                            cheat_message = "Command tidak dikenal."
                        cheat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        cheat_input = cheat_input[:-1]
                    elif event.key >= 32 and event.key <= 126:  # Printable ASCII characters
                        cheat_input += event.unicode
            
            # Continue to next frame, skipping regular game updates
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
                    # Cek apakah enemy dibunuh devil
                    if not getattr(enemy, "killed_by_devil", False):
                        exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                        all_sprites.add(exp)
                        experiences.add(exp)
                        # Tambah uang ke player (solo)
                        player.session_money += 5

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
                        highest_score_menu(screen, player, main_menu_callback, lambda: main(screen, clock, sound_manager, main_menu_callback))
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
                    
                    # Play level up sound
                    sound_manager.play_player_levelup()
                    
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
        
        # --- SESSION TIMER ---
        elapsed_ms = pygame.time.get_ticks() - session_start_ticks - cheat_pause_ticks - pause_ticks
        elapsed_seconds = elapsed_ms // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"

        timer_font = load_font(48)
        timer_surface = render_text_with_border(timer_font, timer_text, WHITE, BLACK)
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 40))
        screen.blit(timer_surface, timer_rect)
        # --- END SESSION TIMER ---

        now = pygame.time.get_ticks()
        if devil is None and now >= next_devil_time:
            devil = Devil(game_map.width, game_map.height)
            all_sprites.add(devil)
            devil_notif_timer = now
            devil_notif_show = True
            # Jadwalkan spawn berikutnya
            if len(devil_spawn_times) == 1:
                devil_spawn_times.append(next_devil_time + 5*60*1000)
            else:
                devil_spawn_times.append(devil_spawn_times[-1] + 5*60*1000)
            next_devil_time = devil_spawn_times[-1]

        if devil:
            devil.update(dt, player.rect, enemies)
            
            # Only show interaction button if devil is active (not fading out or despawning)
            if not getattr(devil, "fading_out", False) and not getattr(devil, "despawning", False):
                # Check if player is in range for interaction
                dx = devil.rect.centerx - player.rect.centerx
                dy = devil.rect.centery - player.rect.centery
                distance = math.hypot(dx, dy)
                
                # Show interaction button when player is in range
                if distance <= devil.damage_circle_radius and devil.is_shop_enabled:
                    interaction_button.show(player)
                else:
                    interaction_button.hide()
                
                # Draw devil indicator when far away
                if distance > 300:
                    angle = math.atan2(dy, dx)
                    arrow_x = WIDTH//2 + math.cos(angle)*180
                    arrow_y = HEIGHT//2 + math.sin(angle)*180
                    pygame.draw.polygon(screen, (255,0,0), [
                        (arrow_x, arrow_y),
                        (arrow_x - 10*math.sin(angle), arrow_y + 10*math.cos(angle)),
                        (arrow_x + 10*math.sin(angle), arrow_y - 10*math.cos(angle)),
                    ])
            else:
                # Hide button if devil is fading out or despawning
                interaction_button.hide()
            
            # Draw the devil in layers to ensure proper ordering
            devil.draw_damage_circle(screen, (camera.x, camera.y))
            devil.draw_shadow(screen, (camera.x, camera.y))
            devil.draw_character(screen, (camera.x, camera.y))
        
        # Notif
        if devil_notif_show and pygame.time.get_ticks() - devil_notif_timer < 2500:
            notif_font = load_font(36)
            notif = notif_font.render("The Devil want to speak with you!", True, (255,50,50))
            notif_rect = notif.get_rect(center=(WIDTH//2, HEIGHT//2-120))
            screen.blit(notif, notif_rect)
        else:
            devil_notif_show = False

        # Draw interaction button after drawing player (should be on top)
        interaction_button.draw(screen, (camera.x, camera.y))
        
        pygame.display.flip()

    return