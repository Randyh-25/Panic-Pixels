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
from ui import SplitScreenUI, render_text_with_border, InteractionButton, MiniMap
from settings import load_font
from particles import ParticleSystem
from partner import Partner
from player2 import Player2
from hit_effects import RockHitEffect
from devil import Devil
from gollux_boss import Gollux  # Import Gollux boss class
from bi_enemy import BiEnemy
from bi_projectile import BiProjectile

def create_blur_surface(surface):
    scale = 0.25 # skala pengecilan untuk menciptakan efek blur
    small_surface = pygame.transform.scale(surface, 
        (int(surface.get_width() * scale), int(surface.get_height() * scale))) # mengecilkan permukaan
    return pygame.transform.scale(small_surface, 
        (surface.get_width(), surface.get_height())) # memperbesar kembali untuk menghasilkan efek blur

def split_screen_main(screen, clock, sound_manager, main_menu_callback):
    map_path = os.path.join("assets", "maps", "desert", "plain.png") # path ke peta default
    map_type = "desert"  # Default to desert map
    
    cheat_mode = False
    cheat_input = ""
    cheat_message = ""
    original_max_health = None
    original_health = None

    try:
        game_map = Map(map_path) # mencoba memuat peta permainan
    except Exception as e:
        print(f"Error loading map: {e}") # menampilkan pesan error jika gagal memuat peta
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
            # jangan tampilkan jika player sedang mati
            if getattr(p, "is_dying", False):
                continue
            # hitung posisi di layar
            px = p.rect.centerx + (camera.x2 if (camera.split_mode and offset_x > 0) else camera.x)
            py = p.rect.top + (camera.y2 if (camera.split_mode and offset_x > 0) else camera.y)
            label_surface = font_label.render(label, True, color)
            label_rect = label_surface.get_rect(center=(px, py - 18))
            viewport_surface.blit(label_surface, label_rect)

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

    # create projectile pools for both player
    MAX_PROJECTILES = 20 # jumlah maksimum proyektil yang disiapkan untuk setiap pemain
    projectile_pool1 = []
    projectile_pool2 = []
    
    for _ in range(MAX_PROJECTILES):
        for pool, group in [(projectile_pool1, projectiles1), (projectile_pool2, projectiles2)]:
            projectile = Projectile((0,0), (0,0))
            pool.append(projectile)
            all_sprites.add(projectile)
            group.add(projectile)
            projectile.kill() # menghemat resource

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
    devil_spawn_times = [4*60*1000]  # ms, menit ke-4
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
    
    # Boss spawn variabls
    boss = None
    boss_spawned = False
    boss_warning_timer = 0
    show_boss_warning = False
    boss_spawn_time = 5 * 60 * 1000  # 5 minutes

    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # collect events before processing to pass to shop
        current_events = [] menyimpan semua event untuk dikirim ke komponen seperti toko
        for event in pygame.event.get():
            current_events.append(event)
            if event.type == pygame.QUIT:
                running = False # menghentikan loop utama jika pemain menutup jendela
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # menutup toko jika sedang terbuka
                    if devil_shop.is_open:
                        devil_shop.close()
                    else:
                        paused = True # mengaktifkan mode pause
                        pause_start = pygame.time.get_ticks()  # MULAI PAUSE
                        pause_menu(screen, main_menu_callback)
                        paused = False # keluar dari mode pause setelah menu selesai
                        if pause_start is not None:
                            pause_ticks += pygame.time.get_ticks() - pause_start  # TAMBAHKAN DURASI PAUSE
                            pause_start = None # reset nilai waktu mulai pause
                # Add cheat console toggle
                elif event.key == pygame.K_BACKQUOTE:
                    cheat_mode = not cheat_mode # mengaktifkan atau menonaktifkan mode cheat
                    if cheat_mode:
                        cheat_pause_start = pygame.time.get_ticks() # untuk menghitung durasi
                    else:
                        if cheat_pause_start is not None:
                            cheat_pause_ticks += pygame.time.get_ticks() - cheat_pause_start # menambahkan durasi cheat ke total
                            cheat_pause_start = None # reset waktu mulai cheat
                    cheat_input = ""
                    cheat_message = ""
                # menambahkan tombol E untuk membuka toko jika interaksi memungkinkan
                elif event.key == pygame.K_e:
                    if devil and devil.can_interact():
                        devil_shop.open() # membuka tampilan toko devil
        
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

            # proses pembelian jika ada pemain yang aktif
            if devil_shop.is_open and active_player:
                # jika pemain menekan enter atau space, lakukan pembelian item yang dipilih
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                    devil_shop.purchase_item(active_player, active_partner) # proses pembelian

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

        enemy_spawn_timer += 1
        MAX_ENEMIES = 15
        # Only spawn enemies if boss isn't spawned yet
        if enemy_spawn_timer >= 60 and len(enemies) < MAX_ENEMIES and not boss_spawned:
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
                        splitscreen_game_over(screen, player1, player2, main_menu_callback)
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
                
        # Draw minimaps
        mini_map1.adjust_for_split_screen(camera.split_mode, WIDTH//2)
        mini_map2.adjust_for_split_screen(camera.split_mode, WIDTH//2)
        mini_map1.draw(screen, player1, player2, enemies, devil, boss)
        mini_map2.draw(screen, player2, player1, enemies, devil, boss)
                
        # --- BOSS WARNING NOTIFICATION ---
        if show_boss_warning:
            # Draw semi-transparent background
            warning_bg = pygame.Surface((WIDTH, HEIGHT))
            warning_bg.fill((0, 0, 0, 180))  # Black with transparency
            screen.blit(warning_bg, (0, 0))
            
            # Draw warning text
            warning_font = load_font(48)
            warning_text = "A powerful enemy has appeared!"
            warning_surface = warning_font.render(warning_text, True, (255, 0, 0))
            warning_rect = warning_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(warning_surface, warning_rect)
            
            # Draw countdown timer
            remaining_time = (boss_spawn_time - (now - boss_warning_timer)) // 1000
            countdown_text = f"Boss spawns in: {remaining_time}"
            countdown_surface = warning_font.render(countdown_text, True, (255, 255, 0))
            countdown_rect = countdown_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
            screen.blit(countdown_surface, countdown_rect)
            
            # Hide warning after 5 seconds
            if now - boss_warning_timer >= 5000:
                show_boss_warning = False
        # --- END BOSS WARNING NOTIFICATION ---
                
        # Boss spawn section - normal
        if not boss_spawned and elapsed_ms >= boss_spawn_time:
            # In co-op, spawn near the midpoint between two players if both alive
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
            
            # Show boss warning
            boss_warning_timer = pygame.time.get_ticks()
            show_boss_warning = True

        # Cheat section for boss spawn
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

        # --- BI ENEMY SPAWNING LOGIC ---
        game_time_seconds = (pygame.time.get_ticks() - session_start_ticks - pause_ticks) // 1000
        if game_time_seconds > last_second:
            bi_spawn_timer += 1  # Increment every second
            
            # Spawn BiEnemies every 10 seconds
            if bi_spawn_timer >= 10:
                # Spawn 2 BiEnemies for variety
                for _ in range(2):
                    bi_enemy = BiEnemy((
                        random.randint(0, game_map.width),
                        random.randint(0, game_map.height)
                    ))
                    all_sprites.add(bi_enemy)
                    bi_enemies.add(bi_enemy)
                
                bi_spawn_timer = 0  # Reset timer

        # Update and draw BiEnemies
        bi_enemies.update()
        
        # Handle BiProjectile hits
        for proj in bi_projectiles:
            # Check collision with players
            if proj.alive():
                hits = pygame.sprite.spritecollide(proj, [player1, player2], False)
                for player in hits:
                    if player.health > 0:  # Only affect alive players
                        player.health -= proj.damage
                        proj.kill()  # Destroy projectile on hit
                        break  # Exit after first hit (one projectile per player)
        
        # Draw BiProjectiles
        for proj in bi_projectiles:
            if proj.alive():
                proj.draw(screen)
        
        # --- END BI ENEMY LOGIC ---

        # Track game time
        current_second = pygame.time.get_ticks() // 1000
        if current_second > last_second:
            game_time_seconds = current_second
            last_second = current_second

        # Spawn Bi enemies after 1 minute (60 seconds) with a slower spawn rate
        if game_time_seconds >= 60:  # Only spawn Bi after 1 minute
            bi_spawn_timer += 1
            if bi_spawn_timer >= 200 and len(bi_enemies) < 5:  # Slower spawn rate, max 5 Bi enemies
                # Choose which player to spawn near
                target_player = random.choice([player1, player2])
                if target_player.health > 0:  # Only spawn if player is alive
                    bi_enemy = BiEnemy(target_player.rect.center)
                    all_sprites.add(bi_enemy)
                    enemies.add(bi_enemy)  # Add to regular enemies group for collisions
                    bi_enemies.add(bi_enemy)  # Also add to bi_enemies group for specialized updates
                    bi_spawn_timer = 0

        # Update Bi enemies and handle their projectiles
        for bi in bi_enemies:
            target, damage = bi.update(random.choice([player1, player2]) if player1.health > 0 and player2.health > 0 else 
                                  player1 if player1.health > 0 else player2, enemies)
            
            # If Bi needs to create a projectile
            if target and damage > 0:
                # Create a new sting projectile
                start_pos = bi.rect.center
                target_pos = target.rect.center
                
                sting = BiProjectile(start_pos, target_pos, bi.sting_image)
                all_sprites.add(sting)
                bi_projectiles.add(sting)

        # Update Bi projectiles
        bi_projectiles.update()

        # Check for Bi projectiles hitting players
        for player in [player1, player2]:
            if player.health <= 0:
                continue
                
            hits = pygame.sprite.spritecollide(player, bi_projectiles, True)
            for projectile in hits:
                player.health -= projectile.damage
                # Optional: Add hit effect here
                
                if player.health <= 0:
                    player.start_death_animation()
                    if not death_transition:
                        death_transition = True
                        blur_surface = create_blur_surface(screen.copy())

        pygame.display.flip()

    return

# Tambahkan fungsi transisi kemenangan
def victory_transition(surface):
    """Animasi transisi saat mengalahkan boss"""
    # White flash effect
    flash_surface = pygame.Surface((WIDTH, HEIGHT))
    flash_surface.fill((255, 255, 255))
    
    # Efek flash putih dengan fade out
    for alpha in range(255, 0, -5):
        surface_copy = surface.copy()
        flash_surface.set_alpha(alpha)
        surface_copy.blit(flash_surface, (0, 0))
        pygame.display.flip()
        pygame.time.delay(5)
    
    # Efek partikel emas
    gold_particles = []
    for _ in range(200):
        gold_particles.append({
            'x': random.randint(0, WIDTH),
            'y': random.randint(HEIGHT//2, HEIGHT*2),  # Start from bottom half
            'size': random.randint(2, 8),
            'speed': random.uniform(2, 6),
            'color': (
                random.randint(200, 255),  # Red
                random.randint(180, 220),  # Green
                random.randint(0, 100)     # Blue - Low for gold color
            )
        })
    
    # Animasikan partikel selama 1.5 detik
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < 1500:
        surface_copy = surface.copy()
        
        # Update dan gambar partikel
        for p in gold_particles:
            p['y'] -= p['speed']
            pygame.draw.circle(
                surface_copy,
                p['color'],
                (int(p['x']), int(p['y'])),
                p['size']
            )
        
        pygame.display.flip()
        pygame.time.delay(16)  # ~60fps

# Contoh di solo.py atau coop.py
def handle_pause():
    quit_to_menu = pause_menu(screen, sound_manager)
    if quit_to_menu:
        # Kembali ke menu utama
        return True
    else:
        # Lanjutkan game
        return False

