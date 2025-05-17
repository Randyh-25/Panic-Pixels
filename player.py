import pygame
import math
from settings import WIDTH, HEIGHT, BLUE
from utils import load_game_data
from player_animations import PlayerAnimations

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_id = 1
        self.animations = PlayerAnimations()
        
        self.image = self.animations.animations['idle_down'][0]
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        
        self.speed = 5
        self.max_health = 100
        self.health = self.max_health
        self.saved_money, _, self.name = load_game_data()
        self.session_money = 0
        self.xp = 0
        self.max_xp = 100
        self.level = 1
        
        self.facing = 'idle_down'
        self.is_moving = False
        self.last_direction = 'down'
        
        self.is_dying = False
        self.death_frame = 0
        self.death_animation_speed = 0.1
        self.death_timer = 0
        self.was_moving = False
        self.step_timer = 0
        self.step_delay = 300
        self.last_step_time = 0
        
    def get_movement_direction(self, dx, dy):
        if dx > 0:
            if dy > 0:
                self.last_direction = 'down_right'
                return 'walk_down_right'
            elif dy < 0:
                self.last_direction = 'up_right'
                return 'walk_up_right'
            else:
                self.last_direction = 'right'
                return 'walk_right'
        elif dx < 0:
            if dy > 0:
                self.last_direction = 'down_left'
                return 'walk_down_left'
            elif dy < 0:
                self.last_direction = 'up_left'
                return 'walk_up_left'
            else:
                self.last_direction = 'left'
                return 'walk_left'
        elif dy > 0:
            self.last_direction = 'down'
            return 'walk_down'
        elif dy < 0:
            self.last_direction = 'up'
            return 'walk_up'
        
        return self.get_idle_direction()
    
    def get_idle_direction(self):
        return f'idle_{self.last_direction}'
        
    def start_death_animation(self):
        self.is_dying = True
        self.death_frame = 0
        self.death_timer = 0
        
        # Play death sound
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.sound_manager.play_player_death()
        
    def update_death_animation(self, dt):
        if not self.is_dying:
            return False
            
        self.death_timer += dt
        if self.death_timer >= self.death_animation_speed:
            self.death_timer = 0
            self.death_frame += 1
            if self.death_frame < len(self.animations.animations['death']):
                self.image = self.animations.animations['death'][self.death_frame]
                return False
            return True
        return False
        
    def animate(self, dt):
        if self.is_dying:
            return self.update_death_animation(dt)
            
        self.animations.animation_timer += dt
        
        if not self.is_moving:
            current_anim = self.get_idle_direction()
        else:
            current_anim = self.facing
            
        if self.animations.animation_timer >= self.animations.animation_speed:
            self.animations.animation_timer = 0
            self.animations.frame_index = (self.animations.frame_index + 1) % len(self.animations.animations[current_anim])
            self.image = self.animations.animations[current_anim][self.animations.frame_index]

    def play_footstep(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_step_time >= self.step_delay:
            self.sound_manager.play_random_footstep()
            self.last_step_time = current_time

    def update(self):
        if self.is_dying:
            return
            
        old_x = self.rect.x
        old_y = self.rect.y
        
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_s]:
            dy += self.speed
            
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        self.is_moving = dx != 0 or dy != 0
        
        if self.is_moving:
            self.play_footstep()
        
        self.was_moving = self.is_moving
        
        if self.is_moving:
            self.facing = self.get_movement_direction(dx, dy)
            
        self.rect.x += dx
        if hasattr(self, 'game_map') and (
            any(self.rect.colliderect(fence) for fence in self.game_map.fence_rects) or
            any(self.rect.colliderect(tree) for tree in self.game_map.tree_collision_rects)):
            self.rect.x = old_x
            
        self.rect.y += dy
        if hasattr(self, 'game_map') and (
            any(self.rect.colliderect(fence) for fence in self.game_map.fence_rects) or
            any(self.rect.colliderect(tree) for tree in self.game_map.tree_collision_rects)):
            self.rect.y = old_y
            
        self.animate(1/60)

class Camera:
    def __init__(self, map_width, map_height):
        self.x = 0
        self.y = 0
        self.x2 = 0
        self.y2 = 0
        self.map_width = map_width
        self.map_height = map_height
        self.split_mode = False
        self.viewport_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    
    def update(self, player1, player2=None):
        if player2 is None:
            # Solo mode atau satu player mati dalam split screen
            self.x = -player1.rect.centerx + WIDTH // 2
            self.y = -player1.rect.centery + HEIGHT // 2
            self.x = min(0, max(-(self.map_width - WIDTH), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
            self.split_mode = False
            return

        # Calculate distance between players
        distance = math.hypot(
            player1.rect.centerx - player2.rect.centerx,
            player1.rect.centery - player2.rect.centery
        )
        
        # Toggle split screen based on distance
        self.split_mode = distance > WIDTH * 0.6 and player1.health > 0 and player2.health > 0
        
        # If one player is dead, follow the other one only
        if player1.health <= 0 or player2.health <= 0:
            self.split_mode = False
            
            if player1.health <= 0:
                # Follow player 2
                self.x = -player2.rect.centerx + WIDTH // 2
                self.y = -player2.rect.centery + HEIGHT // 2
            else:
                # Follow player 1
                self.x = -player1.rect.centerx + WIDTH // 2
                self.y = -player1.rect.centery + HEIGHT // 2
                
            self.x = min(0, max(-(self.map_width - WIDTH), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
            return

        if self.split_mode:
            # Camera for player 1 (left side)
            self.x = -player1.rect.centerx + WIDTH // 4  # Center player1 in left viewport
            self.y = -player1.rect.centery + HEIGHT // 2
            self.x = min(0, max(-(self.map_width - WIDTH//2), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
            
            # Camera for player 2 (right side) - PERBAIKAN
            # Gunakan WIDTH * 3 // 4 untuk memposisikan player2 di tengah viewport kanan
            self.x2 = -player2.rect.centerx + WIDTH // 4  # Offset viewport kanan
            self.y2 = -player2.rect.centery + HEIGHT // 2
            self.x2 = min(0, max(-(self.map_width - WIDTH//2), self.x2))
            self.y2 = min(0, max(-(self.map_height - HEIGHT), self.y2))
        else:
            # Follow midpoint
            mid_x = (player1.rect.centerx + player2.rect.centerx) // 2
            mid_y = (player1.rect.centery + player2.rect.centery) // 2
            
            self.x = -mid_x + WIDTH // 2
            self.y = -mid_y + HEIGHT // 2
            
            self.x = min(0, max(-(self.map_width - WIDTH), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))

    def apply(self, sprite):
        """Return the position of the sprite relative to the camera."""
        return sprite.rect.x + self.x, sprite.rect.y + self.y