import pygame
import random
import math
import os
from settings import *
from player import Player, Camera
from enemy import Enemy
from projectile import Projectile
from experience import Experience, LevelUpEffect
from utils import pause_menu, splitscreen_game_over
from maps import Map
from ui import HealthBar, MoneyDisplay, XPBar, SplitScreenUI, InteractionButton, render_text_with_border, SkillBar, MiniMap
from settings import load_font
from particles import ParticleSystem
from partner import Partner
from player2 import Player2
from hit_effects import RockHitEffect
from devil import Devil
from gollux_boss import Gollux  # Import Gollux boss class
from bi_enemy import BiEnemy
from bi_projectile import BiProjectile
from skill import update_sound_manager

def create_blur_surface(surface):
    scale = 0.25
    small_surface = pygame.transform.scale(surface, 
        (int(surface.get_width() * scale), int(surface.get_height() * scale)))
    return pygame.transform.scale(small_surface, 
        (surface.get_width(), surface.get_height()))

def split_screen_main(screen, clock, sound_manager, main_menu_callback):
    map_path = os.path.join("assets", "maps", "desert", "plain.png")
    map_type = "desert"  # Default to desert map
    
    cheat_mode = False
    cheat_input = ""
    cheat_message = ""
    original_max_health = None
    original_health = None

    try:
        game_map = Map(map_path)
    except Exception as e:
        print(f"Error loading map: {e}")
        return

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
        
        # Draw the devil's damage circle (if active) - add this block
        if devil:
            # The circle should be drawn behind other sprites
            devil.draw_damage_circle(viewport_surface, (cam_x, cam_y))
        
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
                elif isinstance(sprite, Devil):
                    # For Devil, draw in layers to ensure proper ordering
                    sprite.draw_shadow(viewport_surface, (cam_x, cam_y))
                    sprite.draw_character(viewport_surface, (cam_x, cam_y))
                # Tambahkan kondisi baru untuk Gollux
                elif isinstance(sprite, Gollux):
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

        # Setelah menggambar semua sprite, tambahkan label di atas kepala player
        font_label = load_font(28)
        for p, label, color in [
            (player1, "Player 1", (0, 255, 0)),
            (player2, "Player 2", (255, 180, 0))
        ]:
            # Filter agar hanya tampil di viewport yang sesuai
            if camera.split_mode:
                if offset_x == 0 and getattr(p, "player_id", 1) != 1:
                    continue
                if offset_x > 0 and getattr(p, "player_id", 1) != 2:
                    continue
            # Jangan tampilkan jika player sedang mati
            if getattr(p, "is_dying", False):
                continue
            # Hitung posisi di layar
            px = p.rect.centerx + (camera.x2 if (camera.split_mode and offset_x > 0) else camera.x)
            py = p.rect.top + (camera.y2 if (camera.split_mode and offset_x > 0) else camera.y)
            label_surface = font_label.render(label, True, color)
            label_rect = label_surface.get_rect(center=(px, py - 18))
            viewport_surface.blit(label_surface, label_rect)

        # In the draw_game function, add special handling for fullscreen effects
        # After drawing the map but before UI elements:

        # First draw regular sprites with camera offset
        for sprite in all_sprites:
            if not hasattr(sprite, 'is_fullscreen_effect'):
                # (Your existing sprite drawing code)
                pass

        # Draw fullscreen effects on the entire viewport
        for sprite in all_sprites:
            if hasattr(sprite, 'is_fullscreen_effect') and sprite.is_fullscreen_effect:
                if hasattr(sprite, 'draw'):
                    sprite.draw(viewport_surface)

    # Define victory transition function
    def victory_transition(surface):
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((255, 255, 255))  # White flash for victory
        
        for alpha in range(0, 255, 5):
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)
        
        pygame.time.delay(500)  # Hold the white screen briefly
        
        for alpha in range(255, 0, -5):
            fade_surface.set_alpha(alpha)
            screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(10)

    # Continue with the rest of split_screen_main function
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles1 = pygame.sprite.Group()
    projectiles2 = pygame.sprite.Group()
    experiences = pygame.sprite.Group()
    effects = pygame.sprite.Group()
    bi_enemies = pygame.sprite.Group()
    bi_projectiles = pygame.sprite.Group()

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
    
    partner1 = Partner(player1, sound_manager=sound_manager)
    partner2 = Partner(player2, sound_manager=sound_manager)
    
    all_sprites.add(player1, player2, partner1, partner2)

    # Set player_id for partners
    partner1.player_id = 1
    partner2.player_id = 2

    # Create projectile pools for both players
    MAX_PROJECTILES = 20
    projectile_pool1 = []
    projectile_pool2 = []
    
    # Initialize boss variables
    boss = None
    boss_spawn_time = 5*60*1000  # 5 minutes
    boss_spawned = False
    boss_defeated = False
    show_boss_warning = False
    boss_warning_timer = 0
    
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
    game_time_seconds = 0
    bi_spawn_timer = 0
    last_second = 0
    
    # Initialize split screen UI
    ui = SplitScreenUI(WIDTH, HEIGHT)
    
    death_transition = False
    death_alpha = 0
    blur_surface = None
    FADE_SPEED = 15
    TRANSITION_DELAY = 5
    transition_timer = 0
    
    particle_system = ParticleSystem(WIDTH, HEIGHT)
    
    # Tambahkan inisialisasi devil dan variabel terkait
    devil = None
    devil_spawn_times = [2*60*1000]  # ms, menit ke-4
    next_devil_time = devil_spawn_times[0]
    devil_notif_timer = 0
    devil_notif_show = False

    session_start_ticks = pygame.time.get_ticks()  # Simpan waktu mulai session
    
    pause_ticks = 0
    pause_start = None

    cheat_pause_ticks = 0
    cheat_pause_start = None

    # Add interaction button and shop
    interaction_button1 = InteractionButton()
    interaction_button2 = InteractionButton()
    from ui import DevilShop
    devil_shop = DevilShop(sound_manager)
    
    # Initialize mini maps for both players
    mini_map1 = MiniMap(game_map.width, game_map.height, WIDTH, HEIGHT, player_id=1, position="left")
    mini_map2 = MiniMap(game_map.width, game_map.height, WIDTH, HEIGHT, player_id=2, position="right")
    
    # Initialize skill bars for both players - each with one skill in coop mode
    skill_bar1 = SkillBar(player_id=1, position="left", mode="coop")
    skill_bar1.player = player1  # Add player1 reference
    skill_bar2 = SkillBar(player_id=2, position="right", mode="coop")
    skill_bar2.player = player2  # Add player2 reference
    
    # Create a new sprite group for skill effects
    skill_effects = pygame.sprite.Group()

    # Update sound manager at the beginning
    update_sound_manager(sound_manager)

    # Add a variable to track if enemy spawns should be blocked
    nuke_blocking_spawns = False

    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Update skill cooldowns
        skill_bar1.update(dt)
        skill_bar2.update(dt)
        
        # Collect events before processing to pass to shop
        current_events = []
        for event in pygame.event.get():
            current_events.append(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Player 1 skill activation (key 1 only)
                if event.key == pygame.K_1 and player1.health > 0:
                    skill = skill_bar1.activate_skill()
                    if skill:
                        if skill.name == "Heal":
                            effect = skill.activate(player1, enemies=enemies)
                        elif skill.name == "Nuke":
                            effect = skill.activate(player1, enemies=enemies)
                            if effect:
                                nuke_blocking_spawns = True  # Block enemy spawns
                        else:
                            effect = skill.activate(player1.rect.center, enemies=enemies)
                        if effect:
                            all_sprites.add(effect)
                            skill_effects.add(effect)

                # Player 2 skill activation (right Ctrl instead of numpad 1)
                elif event.key == pygame.K_RCTRL and player2.health > 0:  # Changed from K_KP1 to K_RCTRL
                    skill = skill_bar2.activate_skill()
                    if skill:
                        if skill.name == "Heal":
                            effect = skill.activate(player2, enemies=enemies)
                        elif skill.name == "Nuke":
                            effect = skill.activate(player2, enemies=enemies)
                            if effect:
                                nuke_blocking_spawns = True  # Block enemy spawns
                        else:
                            effect = skill.activate(player2.rect.center, enemies=enemies)
                        if effect:
                            all_sprites.add(effect)
                            skill_effects.add(effect)
                    
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
            # When shop is open, determine which player is interacting
            active_player = None
            active_partner = None

            if interaction_button1.is_visible and interaction_button1.target_entity == player1:
                active_player = player1
                active_partner = partner1
            elif interaction_button2.is_visible and interaction_button2.target_entity == player2:
                active_player = player2
                active_partner = partner2

            # Process purchase if a player is active
            if devil_shop.is_open and active_player:
                # If player presses enter or space, try to purchase the selected item
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                    devil_shop.purchase_item(active_player, active_partner)

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
                            player1.session_money += 10000
                            cheat_message = "Money +10000!"
                        elif cheat_input == "armordaribapak":
                            if original_max_health is None:
                                original_max_health = player1.max_health
                                original_health = player1.health
                            player1.max_health = 1000
                            player1.health = 1000
                            player2.max_health = 1000
                            player2.health = 1000
                            cheat_message = "Armor dari bapak aktif!"
                        elif cheat_input == "rakyatbiasa":
                            if original_max_health is not None:
                                player1.max_health = original_max_health
                                player1.health = original_health
                                player2.max_health = original_max_health
                                player2.health = original_health
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
                        elif cheat_input == "spawnboss":
                            if boss is None:
                                # Spawn near active players
                                if player1.health > 0 and player2.health > 0:
                                    midpoint = ((player1.rect.centerx + player2.rect.centerx) // 2, 
                                               (player1.rect.centery + player2.rect.centery) // 2)
                                    boss = Gollux(game_map.width, game_map.height, midpoint)
                                elif player1.health > 0:
                                    boss = Gollux(game_map.width, game_map.height, player1.rect.center)
                                else:
                                    boss = Gollux(game_map.width, game_map.height, player2.rect.center)
                                    
                                boss.sound_manager = sound_manager  # Set sound manager reference
                                all_sprites.add(boss)
                                boss_spawned = True
                                cheat_message = "Gollux boss spawned!"
                            else:
                                cheat_message = "Boss sudah ada!"
                        else:
                            cheat_message = "Command tidak dikenal."
                        cheat_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        cheat_input = cheat_input[:-1]
                    elif event.key >= 32 and event.key <= 126:  # Printable ASCII characters
                        cheat_input += event.unicode
            
            # Continue to next frame, skipping regular game updates
            continue

        # Spawn enemies
        enemy_spawn_timer += 1
        MAX_ENEMIES = 15
        # Only spawn enemies if boss isn't spawned yet
        if enemy_spawn_timer >= 60 and len(enemies) < MAX_ENEMIES and not boss_spawned:
            # Add check for nuke blocking
            spawn_blocked = False
            for effect in skill_effects:
                if hasattr(effect, 'block_enemy_spawns') and effect.block_enemy_spawns:
                    spawn_blocked = True
                    break
    
            if not spawn_blocked:
                enemy = Enemy((
                    (player1.rect.centerx + player2.rect.centerx) // 2,
                    (player1.rect.centery + player2.rect.centery) // 2
                ))
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_spawn_timer = 0
            
        # Also fix partner shooting in split screen mode
        projectile_timer += 1
        # Ubah kondisi menjadi memeriksa boss atau enemies
        if projectile_timer >= 30 and (len(enemies) > 0 or (boss is not None and not boss.is_defeated)):
            # Handle partner1 shooting
            if player1.health > 0:
                closest_enemy = None
                min_dist = float('inf')
                shoot_radius = 500
                
                # First check if boss exists and target it with priority
                if boss and not boss.is_defeated:
                    dist = math.hypot(boss.rect.centerx - player1.rect.centerx,
                                     boss.rect.centery - player1.rect.centery)
                    if dist < shoot_radius:
                        closest_enemy = boss
                        min_dist = dist
                # Jika tidak ada boss atau boss terlalu jauh, coba target musuh biasa
                if closest_enemy is None:
                    for enemy in enemies:
                        if enemy.is_dying:
                            continue
                            
                        dist = math.hypot(enemy.rect.centerx - player1.rect.centerx,
                                        enemy.rect.centery - player1.rect.centery)
                        if dist < min_dist and dist < shoot_radius:
                            min_dist = dist
                            closest_enemy = enemy
                
                if closest_enemy:
                    for projectile in projectile_pool1:
                        if not projectile.alive():
                            start_pos = partner1.get_shooting_position()
                            target_pos = (closest_enemy.rect.centerx, closest_enemy.rect.centery)
                            
                            partner1.shoot_at(target_pos)  # This will now play the sound
                            
                            # Get projectile type based on partner type
                            projectile_type = partner1.get_projectile_type()
                            
                            projectile.reset(start_pos, target_pos, projectile_type)
                            projectile.add(all_sprites, projectiles1)
                            break
                else:
                    partner1.stop_shooting()
            
            # Handle partner2 shooting (lakukan perubahan serupa)
            if player2.health > 0:
                closest_enemy = None
                min_dist = float('inf')
                shoot_radius = 500
                
                # First check if boss exists and target it with priority
                if boss and not boss.is_defeated:
                    dist = math.hypot(boss.rect.centerx - player2.rect.centerx,
                                     boss.rect.centery - player2.rect.centery)
                    if dist < shoot_radius:
                        closest_enemy = boss
                        min_dist = dist
                # Jika tidak ada boss atau boss terlalu jauh, coba target musuh biasa
                if closest_enemy is None:
                    for enemy in enemies:
                        if enemy.is_dying:
                            continue
                            
                        dist = math.hypot(enemy.rect.centerx - player2.rect.centerx,
                                        enemy.rect.centery - player2.rect.centery)
                        if dist < min_dist and dist < shoot_radius:
                            min_dist = dist
                            closest_enemy = enemy
                
                if closest_enemy:
                    for projectile in projectile_pool2:
                        if not projectile.alive():
                            start_pos = partner2.get_shooting_position()
                            target_pos = (closest_enemy.rect.centerx, closest_enemy.rect.centery)
                            
                            partner2.shoot_at(target_pos)
                            
                            # Get projectile type based on partner type
                            projectile_type = partner2.get_projectile_type()
                            
                            projectile.reset(start_pos, target_pos, projectile_type)
                            projectile.add(all_sprites, projectiles2)
                            break
                else:
                    partner2.stop_shooting()
                    
            projectile_timer = 0

        player1.update(dt)
        player2.update(dt)
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
            # Deteksi tumbukan dengan musuh biasa
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
                        # Cek apakah enemy dibunuh devil
                        if not getattr(enemy, "killed_by_devil", False):
                            exp = Experience(enemy.rect.centerx, enemy.rect.centery)
                            all_sprites.add(exp)
                            experiences.add(exp)
                            # Tambah uang ke player (coop - dibagi rata)
                            player1.session_money += 3
                            player2.session_money += 2

            # Deteksi tumbukan dengan boss
            if boss and not boss.is_defeated:
                hits = pygame.sprite.spritecollide(boss, projs, True)
                for projectile in hits:
                    # Add hit effect
                    hit_effect = RockHitEffect((boss.rect.centerx, boss.rect.centery))
                    all_sprites.add(hit_effect)
                    effects.add(hit_effect)
                    
                    # Deal damage to boss
                    boss_defeated = boss.take_hit(projectile.damage)
                    
                    # If boss is defeated, trigger victory
                    if boss_defeated:
                        # Hitung skor dan waktu bermain
                        elapsed_ms = pygame.time.get_ticks() - session_start_ticks - cheat_pause_ticks - pause_ticks
                        elapsed_seconds = elapsed_ms // 1000
                        
                        # Tambahkan reward uang untuk kedua pemain
                        player1.session_money += 1000
                        player2.session_money += 1000
                        
                        total_score = player1.session_money + player2.session_money
                        
                        # Transisi kemenangan
                        victory_transition(screen)
                        
                        # Tampilkan layar kemenangan dengan pesan kustom
                        show_victory_screen(screen, total_score, elapsed_seconds, sound_manager,
                                           "You've defeated Gollux together! The world is saved!")
                        return

        # Handle death transition
        if death_transition:
            both_players_dead = player1.health <= 0 and player2.health <= 0
    
            if player1.health <= 0:
                player1.update_death_animation(dt)
            if player2.health <= 0:
                player2.update_death_animation(dt)
            
            # Check if both players are dead and both animations are complete or if enough time has passed
            animation_complete = (player1.health <= 0 and player2.health <= 0 and 
                                 (getattr(player1, 'death_animation_complete', False) or 
                                  getattr(player2, 'death_animation_complete', False)))
            
            if animation_complete:
                # Proceed with game over
                death_alpha += FADE_SPEED
                if death_alpha >= 255:
                    transition_timer += 1
                    if transition_timer >= TRANSITION_DELAY:
                        # Show game over
                        splitscreen_game_over(screen, player1, player2, main_menu_callback, split_screen_main)
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
                    
                    # Play level up sound
                    sound_manager.play_player_levelup()
                    
                    level_effect = LevelUpEffect(player)
                    effects.add(level_effect)
                    all_sprites.add(level_effect)

        # Update camera to follow midpoint between players
        if player1.health <= 0:
            # Player 1 mati, kamera ikuti player 2
            if player2 is not None and hasattr(player2, 'rect'):
                camera.update(player2)
            else:
                # Fallback to player1 if available, or do nothing
                if player1 is not None and hasattr(player1, 'rect'):
                    camera.update(player1)
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
            
            # Right viewport (Player 2)
            right_viewport = pygame.Rect(WIDTH//2 + divider_width//2, 0, WIDTH//2 - divider_width//2, HEIGHT)
            draw_game(right_viewport, WIDTH//2, 2)  # Draw with player 2 filter
            
            # Draw UI for both players
            ui.draw_split(screen, player1, player2, True)
        else:
            # Normal single screen drawing
            full_viewport = pygame.Rect(0, 0, WIDTH, HEIGHT)
            draw_game(full_viewport)
            ui.draw(screen, player1, player2)

        # --- SESSION TIMER ---
        elapsed_ms = pygame.time.get_ticks() - session_start_ticks - pause_ticks
        elapsed_seconds = elapsed_ms // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"

        timer_font = load_font(48)
        timer_surface = render_text_with_border(timer_font, timer_text, WHITE, BLACK)
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 40))
        screen.blit(timer_surface, timer_rect)

        # Check for devil spawn
        now = pygame.time.get_ticks()
        if devil is None and now >= next_devil_time:
            devil = Devil(game_map.width, game_map.height)
            all_sprites.add(devil)
            devil_notif_timer = now
            devil_notif_show = True
            # Jadwalkan spawn berikutnya
            if len(devil_spawn_times) == 1:
                devil_spawn_times.append(next_devil_time + 2*60*1000)
            else:
                devil_spawn_times.append(devil_spawn_times[-1] + 2*60*1000)
            next_devil_time = devil_spawn_times[-1]

        # Update devil if it exists
        if devil:
            # Update using the correct player
            if player1.health <= 0:
                active_player = player2
            elif player2.health <= 0:
                active_player = player1
            else:
                active_player = player1  # Default to player1 when both alive
                
            devil.update(dt, active_player.rect, enemies)
            
            # Draw devil indicator regardless of devil state
            # In split screen, check which player is alive and draw indicator accordingly
            if camera.split_mode:
                # For player 1 (left viewport)
                if player1.health > 0:
                    p1_dx = devil.rect.centerx - player1.rect.centerx
                    p1_dy = devil.rect.centery - player1.rect.centery
                    p1_dist = math.hypot(p1_dx, p1_dy)
                    
                    if p1_dist > 300:
                        angle = math.atan2(p1_dy, p1_dx)
                        arrow_x = (WIDTH//4) + math.cos(angle)*100
                        arrow_y = HEIGHT//2 + math.sin(angle)*100
                        pygame.draw.polygon(screen, (255,0,0), [
                            (arrow_x, arrow_y),
                            (arrow_x - 10*math.sin(angle), arrow_y + 10*math.cos(angle)),
                            (arrow_x + 10*math.sin(angle), arrow_y - 10*math.cos(angle)),
                        ])
                        
                # For player 2 (right viewport)
                if player2.health > 0:
                    p2_dx = devil.rect.centerx - player2.rect.centerx
                    p2_dy = devil.rect.centery - player2.rect.centery
                    p2_dist = math.hypot(p2_dx, p2_dy)
                    
                    if p2_dist > 300:
                        angle = math.atan2(p2_dy, p2_dx)
                        arrow_x = (WIDTH*3//4) + math.cos(angle)*100
                        arrow_y = HEIGHT//2 + math.sin(angle)*100
                        pygame.draw.polygon(screen, (255,0,0), [
                            (arrow_x, arrow_y),
                            (arrow_x - 10*math.sin(angle), arrow_y + 10*math.cos(angle)),
                            (arrow_x + 10*math.sin(angle), arrow_y - 10*math.cos(angle)),
                        ])
            else:
                dx = devil.rect.centerx - active_player.rect.centerx
                dy = devil.rect.centery - active_player.rect.centery
                dist = math.hypot(dx, dy)
                
                if dist > 300:
                    angle = math.atan2(dy, dx)
                    arrow_x = WIDTH//2 + math.cos(angle)*180
                    arrow_y = HEIGHT//2 + math.sin(angle)*180
                    pygame.draw.polygon(screen, (255,0,0), [
                        (arrow_x, arrow_y),
                        (arrow_x - 10*math.sin(angle), arrow_y + 10*math.cos(angle)),
                        (arrow_x + 10*math.sin(angle), arrow_y - 10*math.cos(angle)),
                    ])
                
            # Only show interaction button if devil is active (not fading out or despawning)
            if not getattr(devil, "fading_out", False) and not getattr(devil, "despawning", False):
                # Check for player1 interaction
                if player1.health > 0:
                    p1_dx = devil.rect.centerx - player1.rect.centerx
                    p1_dy = devil.rect.centery - player1.rect.centery
                    p1_dist = math.hypot(p1_dx, p1_dy)
                    
                    if p1_dist <= devil.damage_circle_radius and devil.is_shop_enabled:
                        interaction_button1.show(player1)
                    else:
                        interaction_button1.hide()
                
                # Check for player2 interaction
                if player2.health > 0:
                    p2_dx = devil.rect.centerx - player2.rect.centerx
                    p2_dy = devil.rect.centery - player2.rect.centery
                    p2_dist = math.hypot(p2_dx, p2_dy)
                    
                    if p2_dist <= devil.damage_circle_radius and devil.is_shop_enabled:
                        interaction_button2.show(player2)
                    else:
                        interaction_button2.hide()
            else:
                # Hide buttons if devil is fading out or despawning
                interaction_button1.hide()
                interaction_button2.hide()
        
        # Notif
        if devil_notif_show and pygame.time.get_ticks() - devil_notif_timer < 2500:
            notif_font = load_font(36)
            notif = notif_font.render("The Devil want to speak with you!", True, (255,50,50))
            notif_rect = notif.get_rect(center=(WIDTH//2, HEIGHT//2-120))
            screen.blit(notif, notif_rect)
        else:
            devil_notif_show = False

        # Draw interaction buttons on appropriate viewports
        if camera.split_mode:
            # For left viewport
            if interaction_button1.is_visible:
                interaction_button1.draw(screen.subsurface(left_viewport), (camera.x, camera.y))
                
            # For right viewport
            if interaction_button2.is_visible:
                interaction_button2.draw(screen.subsurface(right_viewport), (camera.x2, camera.y2))
        else:
            # For single view
            if interaction_button1.is_visible:
                interaction_button1.draw(screen, (camera.x, camera.y))
            if interaction_button2.is_visible:  
                interaction_button2.draw(screen, (camera.x, camera.y))
                
        # Update minimaps and skill positions based on split screen mode
        mini_map1.adjust_for_split_screen(camera.split_mode, WIDTH//2)
        mini_map2.adjust_for_split_screen(camera.split_mode, WIDTH//2)
        skill_bar1.adjust_position(camera.split_mode, WIDTH)
        skill_bar2.adjust_position(camera.split_mode, WIDTH)
        
        # Draw UI elements
        if camera.split_mode:
            # For split screen mode
            # Left half (player 1)
            left_viewport = pygame.Rect(0, 0, WIDTH//2 - divider_width//2, HEIGHT)
            mini_map1.draw(screen, player1, player2, enemies, devil, boss)
            skill_bar1.draw(screen)
            
            # Right half (player 2)
            right_viewport = pygame.Rect(WIDTH//2 + divider_width//2, 0, WIDTH//2 - divider_width//2, HEIGHT)
            mini_map2.draw(screen, player2, player1, enemies, devil, boss)
            skill_bar2.draw(screen)
        else:
            # Single screen mode
            mini_map1.draw(screen, player1, player2, enemies, devil, boss)
            mini_map2.draw(screen, player2, player1, enemies, devil, boss)
            skill_bar1.draw(screen)
            if player2.health > 0:
                skill_bar2.draw(screen)
        
        # --- SESSION TIMER ---
        elapsed_ms = pygame.time.get_ticks() - session_start_ticks - pause_ticks
        elapsed_seconds = elapsed_ms // 1000
        minutes = elapsed_seconds // 60
        seconds = elapsed_seconds % 60
        timer_text = f"{minutes:02d}:{seconds:02d}"

        timer_font = load_font(48)
        timer_surface = render_text_with_border(timer_font, timer_text, WHITE, BLACK)
        timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 40))
        screen.blit(timer_surface, timer_rect)

        # Check if boss should spawn based on elapsed time
        elapsed_time = pygame.time.get_ticks() - session_start_ticks - pause_ticks - cheat_pause_ticks
        if not boss_spawned and not boss_defeated and elapsed_time >= boss_spawn_time:
            # Create midpoint between active players
            if player1.health > 0 and player2.health > 0:
                midpoint = ((player1.rect.centerx + player2.rect.centerx) // 2, 
                           (player1.rect.centery + player2.rect.centery) // 2)
            elif player1.health > 0:
                midpoint = player1.rect.center
            else:
                midpoint = player2.rect.center
                
            # Create and setup boss
            boss = Gollux(game_map.width, game_map.height, midpoint)
            boss.sound_manager = sound_manager
            all_sprites.add(boss)
            boss_spawned = True
            
            # Show boss warning
            boss_warning_timer = pygame.time.get_ticks()
            show_boss_warning = True
            
        # Display boss warning if active
        if show_boss_warning:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - boss_warning_timer
            
            if elapsed_time < 3000:  # Show for 3 seconds
                warning_font = load_font(48)
                warning_text = warning_font.render("BOSS APPROACHING!", True, (255, 0, 0))
                warning_rect = warning_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
                
                # Add pulsing effect
                pulse = math.sin(current_time * 0.01) * 10 + 255
                pulse = max(0, min(255, pulse))
                warning_text.set_alpha(pulse)
                
                screen.blit(warning_text, warning_rect)
            else:
                show_boss_warning = False
            
        pygame.display.flip()

    return