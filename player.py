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
        self.death_animation_complete = False  # Add this missing attribute
        self.was_moving = False
        self.step_timer = 0
        self.step_delay = 300
        self.last_step_time = 0
        
        # New attributes for speed boost and health regeneration
        self.speed_boost_timer = 0
        self.speed_multiplier = 1.0
        self.regen_timer = 0
        self.regen_amount = 0

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
        self.death_animation_complete = False  # Make sure this flag is reset
        
        # Play death sound
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.sound_manager.play_player_death()

    def update_death_animation(self, dt):
        if not self.is_dying:
            return False

        # Only process if the animation isn't already complete
        if not self.death_animation_complete:
            self.death_timer += dt # menambah timer kematian dengan delta waktu
            if self.death_timer >= self.death_animation_speed:
                self.death_timer = 0 # mereset timer animasi kematian
                self.death_frame += 1 # menaikkan index frame kematian
                if self.death_frame < len(self.animations.animations['death']):
                    self.image = self.animations.animations['death'][self.death_frame]
                else:
                    # Set the flag when animation completes
                    self.death_animation_complete = True # menandai animasi kematian sudah selesai
                    # Keep the last frame visible
                    self.death_frame = len(self.animations.animations['death']) - 1 # tetap di frame trakhir animasi kematian
                    self.image = self.animations.animations['death'][self.death_frame] # set gambar ke frame terakhir
                    return True
    
        # Return True if animation has completed, False otherwise
        return self.death_animation_complete

    def animate_death(self):
        # Progress the death animation
        if self.death_animation_timer >= self.animation_speed:
            self.death_animation_timer = 0
            self.current_death_frame += 1
            
            # Ensure we don't exceed animation frames
            if self.current_death_frame >= len(self.animations['death']):
                self.current_death_frame = len(self.animations['death']) - 1
                self.death_animation_complete = True

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

    def update(self, dt, game_map_rect=None):
        if self.is_dying:
            return
            
        old_x = self.rect.x
        old_y = self.rect.y
        
        dx = 0
        dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_s]:
            dy += 1
            
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        self.is_moving = dx != 0 or dy != 0
        
        if self.is_moving:
            self.play_footstep()
        
        self.was_moving = self.is_moving
        
        if self.is_moving:
            self.facing = self.get_movement_direction(dx, dy)
            
        # Handle speed boost
        if self.speed_boost_timer > 0:
            self.speed_boost_timer -= dt
            actual_speed = self.speed * self.speed_multiplier
        else:
            self.speed_multiplier = 1.0
            actual_speed = self.speed
        
        # Handle health regeneration
        if self.regen_timer > 0:
            self.regen_timer -= dt
            self.regen_cooldown -= dt
            if self.regen_cooldown <= 0:
                self.health = min(self.health + self.regen_amount, self.max_health)
                self.regen_cooldown = 1  # Regenerate once per second
    
        # Apply delta time to movement to ensure consistent speed across different frame rates
        frame_speed = actual_speed * dt * 60  # Normalize to 60fps
    
        self.rect.x += dx * frame_speed
        if hasattr(self, 'game_map') and (
            any(self.rect.colliderect(fence) for fence in self.game_map.fence_rects) or
            any(self.rect.colliderect(tree) for tree in self.game_map.tree_collision_rects)):
            self.rect.x = old_x
            
        self.rect.y += dy * frame_speed
        if hasattr(self, 'game_map') and (
            any(self.rect.colliderect(fence) for fence in self.game_map.fence_rects) or
            any(self.rect.colliderect(tree) for tree in self.game_map.tree_collision_rects)):
            self.rect.y = old_y
            
        self.animate(dt)

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
        # Add check at the beginning of the method to prevent None errors
        if player1 is None:
            return
            
        # If only one player is provided, use single player camera mode
        if player2 is None:
            self.split_mode = False
            target_player = player1
            self.x = -target_player.rect.centerx + WIDTH // 2
            self.y = -target_player.rect.centery + HEIGHT // 2
            self.x = min(0, max(-(self.map_width - WIDTH), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
            return
            
        previous_split_mode = self.split_mode
        
        # Calculate distance between players
        distance = math.hypot(
            player1.rect.centerx - player2.rect.centerx,
            player1.rect.centery - player2.rect.centery
        )
        
        # Toggle split screen based on distance
        new_split_mode = distance > WIDTH * 0.6
        
        # Store previous positions for smooth transition
        if new_split_mode != previous_split_mode:
            if new_split_mode:  # Going from single to split screen
                # Calculate the center point between players
                center_x = (player1.rect.centerx + player2.rect.centerx) // 2
                center_y = (player1.rect.centery + player2.rect.centery) // 2
                
                # Calculate positions for split screen using the same center reference
                # This preserves the relative positions when transitioning
                self.x = -center_x + WIDTH // 2
                self.y = -center_y + HEIGHT // 2
                
                # Initialize split screen camera positions at the same center point
                # but adjusted for the split screen width
                self.x1 = -player1.rect.centerx + WIDTH // 4
                self.y1 = -player1.rect.centery + HEIGHT // 2
                self.x2 = -player2.rect.centerx + WIDTH // 4
                self.y2 = -player2.rect.centery + HEIGHT // 2
                
                # Apply boundaries
                self.x1 = min(0, max(-(self.map_width - WIDTH//2), self.x1))
                self.y1 = min(0, max(-(self.map_height - HEIGHT), self.y1))
                self.x2 = min(0, max(-(self.map_width - WIDTH//2), self.x2))
                self.y2 = min(0, max(-(self.map_height - HEIGHT), self.y2))
            else:  # Going from split to single screen
                # When merging views, use the midpoint between players
                center_x = (player1.rect.centerx + player2.rect.centerx) // 2
                center_y = (player1.rect.centery + player2.rect.centery) // 2
                
                self.x = -center_x + WIDTH // 2
                self.y = -center_y + HEIGHT // 2
                self.x = min(0, max(-(self.map_width - WIDTH), self.x))
                self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
    
        self.split_mode = new_split_mode
        
        if self.split_mode:
            # Update player 1's viewport (left side)
            self.x = -player1.rect.centerx + WIDTH // 4
            self.y = -player1.rect.centery + HEIGHT // 2
            self.x = min(0, max(-(self.map_width - WIDTH//2), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))
            
            # Update player 2's viewport (right side)
            self.x2 = -player2.rect.centerx + WIDTH // 4
            self.y2 = -player2.rect.centery + HEIGHT // 2
            self.x2 = min(0, max(-(self.map_width - WIDTH//2), self.x2))
            self.y2 = min(0, max(-(self.map_height - HEIGHT), self.y2))
        else:
            # In single screen mode, follow the midpoint between players
            center_x = (player1.rect.centerx + player2.rect.centerx) // 2
            center_y = (player1.rect.centery + player2.rect.centery) // 2
            
            self.x = -center_x + WIDTH // 2
            self.y = -center_y + HEIGHT // 2
            self.x = min(0, max(-(self.map_width - WIDTH), self.x))
            self.y = min(0, max(-(self.map_height - HEIGHT), self.y))

    def apply(self, sprite):
        """Return the position of the sprite relative to the camera."""
        return sprite.rect.x + self.x, sprite.rect.y + self.y
