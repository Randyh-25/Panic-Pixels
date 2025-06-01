import pygame
import os
import random
import math

# List of available skill names that can be assigned to players
available_skills = ["thunder_strike", "heal", "nuke"]

class Skill:
    """Base class for all skills"""
    def __init__(self, sound_manager=None):
        self.name = "Base Skill"
        self.description = "Base skill description"
        self.price = 0
        self.cooldown = 0
        self.icon = None
        self.sound_manager = sound_manager
        self.damage = 0
    
    def activate(self, player_pos, target_pos=None, enemies=None):
        """Activate skill at player position, optionally targeting a position"""
        pass
    
    def get_icon(self):
        """Returns the skill UI icon"""
        return self.icon

    # Add this function to your skill.py file - make sure it's at the module level (not nested in a class)
def update_sound_manager(sound_manager):
    """Add skill sound methods to the sound manager"""
    # Method to play thunder strike sound
    def play_thunder_strike(self):
        path = os.path.join("assets", "sound", "skill", "thunder_strike.ogg")
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.7)  # Adjust volume as needed
            sound.play()
    
    # Method to play heal sound
    def play_heal(self):
        path = os.path.join("assets", "sound", "skill", "heal.ogg")
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.7)  # Adjust volume as needed
            sound.play()
    
    # Method to play nuke sound
    def play_nuke(self):
        path = os.path.join("assets", "sound", "skill", "nuke.ogg")
        if os.path.exists(path):
            sound = pygame.mixer.Sound(path)
            sound.set_volume(0.8)  # Slightly louder due to its importance
            sound.play()
    
    # Generic method to play any skill sound
    def play_skill_sound(self, skill_name):
        method_name = f"play_{skill_name}"
        if hasattr(self, method_name):
            getattr(self, method_name)()
    
    # Add methods to sound manager
    sound_manager.play_thunder_strike = play_thunder_strike.__get__(sound_manager)
    sound_manager.play_heal = play_heal.__get__(sound_manager)
    sound_manager.play_nuke = play_nuke.__get__(sound_manager)
    sound_manager.play_skill_sound = play_skill_sound.__get__(sound_manager)



class ThunderStrike(Skill):
    """Thunder Strike skill that creates lightning damage in an area"""
    def __init__(self, sound_manager=None):
        super().__init__(sound_manager)
        self.name = "Thunder Strike"
        self.description = "Call lightning from the sky to strike enemy crowds"
        self.price = 500
        self.cooldown = 8.0  # 8 seconds cooldown
        self.damage = 50  # Base damage
        self.area_radius = 120  # Damage radius
        
        # Load skill icon for UI
        self.icon_path = os.path.join("assets", "UI", "skill", "thunder_strike.png")
        self.icon = pygame.image.load(self.icon_path).convert_alpha() if os.path.exists(self.icon_path) else None
        
        # Load animation frames
        self.frames = []
        for i in range(1, 6):  # thunder (1).png through thunder (5).png
            path = os.path.join("assets", "skill", "thunder_strike", f"thunder ({i}).png")
            if os.path.exists(path):
                frame = pygame.image.load(path).convert_alpha()
                self.frames.append(frame)
        
        # Sound effect path
        self.sound_path = os.path.join("assets", "sound", "skill", "thunder_strike.ogg")
    
    def activate(self, player_pos, target_pos=None, enemies=None):
        """Activate thunder strike at best location targeting enemy crowds"""
        if not enemies or len(enemies) == 0:
            # Fallback to player direction if no enemies
            if hasattr(player_pos, 'last_direction'):
                direction = player_pos.last_direction
                offset = 150  # Distance from player
                
                # Calculate target position based on player's facing direction
                target_x, target_y = player_pos.rect.center
                
                if 'right' in direction:
                    target_x += offset
                elif 'left' in direction:
                    target_x -= offset
                    
                if 'up' in direction:
                    target_y -= offset
                elif 'down' in direction:
                    target_y += offset
                    
                # Adjust diagonal distance to keep consistent range
                if 'up' in direction and ('left' in direction or 'right' in direction):
                    offset = offset * 0.7071  # sqrt(2)/2
                    
                if 'down' in direction and ('left' in direction or 'right' in direction):
                    offset = offset * 0.7071  # sqrt(2)/2
                
                target_pos = (target_x, target_y)
            else:
                target_pos = player_pos.rect.center if hasattr(player_pos, 'rect') else player_pos
        else:
            # Find the best position to hit the most enemies
            best_pos = self._find_optimal_target(player_pos, enemies)
            target_pos = best_pos
            
        # Play thunder sound
        if self.sound_manager:
            self.sound_manager.play_skill_sound("thunder_strike")
            
        # Create and return the visual effect
        effect = ThunderStrikeEffect(target_pos, self.frames, self.damage, self.area_radius)
        
        # Deal damage to enemies immediately if provided
        if enemies:
            effect.deal_damage(enemies)
            
        return effect
    
    def _find_optimal_target(self, player_pos, enemies):
        """Find the optimal target position that hits the most enemies"""
        player_center = player_pos.rect.center if hasattr(player_pos, 'rect') else player_pos
        player_x, player_y = player_center
        
        # Group enemies by proximity to each other
        # We'll use a grid-based approach to find enemy clusters
        
        # First, identify if there are any clear clusters
        best_count = 0
        best_pos = player_center  # Default to player position
        max_range = 350  # Maximum range from player
        
        # Test each enemy as a potential center point
        for enemy in enemies:
            if hasattr(enemy, 'is_dying') and enemy.is_dying:
                continue
                
            # Skip if enemy is too far from player
            distance_to_player = math.hypot(
                enemy.rect.centerx - player_x,
                enemy.rect.centery - player_y
            )
            
            if distance_to_player > max_range:
                continue
                
            # Count enemies within radius of this enemy
            enemy_x, enemy_y = enemy.rect.center
            count = 0
            
            for other in enemies:
                if hasattr(other, 'is_dying') and other.is_dying:
                    continue
                    
                distance = math.hypot(
                    other.rect.centerx - enemy_x,
                    other.rect.centery - enemy_y
                )
                
                if distance <= self.area_radius:
                    count += 1
            
            # If this position hits more enemies, use it
            if count > best_count:
                best_count = count
                best_pos = (enemy_x, enemy_y)
        
        # If no good cluster was found or only hitting 1 enemy, 
        # try to find a better position between enemies
        if best_count <= 1 and len(enemies) > 1:
            # Try some positions between groups of enemies
            sample_size = min(5, len(enemies))
            enemy_sample = random.sample(list(enemies), sample_size)
            
            for i in range(len(enemy_sample)):
                for j in range(i+1, len(enemy_sample)):
                    # Try a point between these two enemies
                    e1 = enemy_sample[i]
                    e2 = enemy_sample[j]
                    
                    # Skip dying enemies
                    if (hasattr(e1, 'is_dying') and e1.is_dying) or (hasattr(e2, 'is_dying') and e2.is_dying):
                        continue
                    
                    # Get midpoint
                    mid_x = (e1.rect.centerx + e2.rect.centerx) // 2
                    mid_y = (e1.rect.centery + e2.rect.centery) // 2
                    
                    # Check if midpoint is in range
                    distance_to_player = math.hypot(mid_x - player_x, mid_y - player_y)
                    if distance_to_player > max_range:
                        continue
                    
                    # Count enemies hit by this position
                    count = 0
                    for other in enemies:
                        if hasattr(other, 'is_dying') and other.is_dying:
                            continue
                            
                        distance = math.hypot(
                            other.rect.centerx - mid_x,
                            other.rect.centery - mid_y
                        )
                        
                        if distance <= self.area_radius:
                            count += 1
                    
                    if count > best_count:
                        best_count = count
                        best_pos = (mid_x, mid_y)
        
        # If we still don't have a good position, use the closest enemy
        if best_count == 0:
            closest_enemy = None
            closest_dist = float('inf')
            
            for enemy in enemies:
                if hasattr(enemy, 'is_dying') and enemy.is_dying:
                    continue
                    
                distance = math.hypot(
                    enemy.rect.centerx - player_x,
                    enemy.rect.centery - player_y
                )
                
                if distance < closest_dist and distance <= max_range:
                    closest_dist = distance
                    closest_enemy = enemy
            
            if closest_enemy:
                best_pos = closest_enemy.rect.center
        
        return best_pos


class ThunderStrikeEffect(pygame.sprite.Sprite):
    """Visual effect for Thunder Strike skill"""
    def __init__(self, position, frames, damage, radius):
        super().__init__()
        self.position = position
        self.frames = frames
        self.damage = damage
        self.radius = radius
        
        # Animation properties
        self.frame_index = 0
        self.animation_speed = 0.1  # Time between frames in seconds
        self.animation_timer = 0
        self.image = self.frames[0] if self.frames else None
        
        if self.image:
            self.rect = self.image.get_rect(center=self.position)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
        
        self.finished = False
        self.has_dealt_damage = False
        
        # Fade out properties
        self.fading_out = False
        self.fade_duration = 0.3  # Fade duration in seconds
        self.fade_timer = 0
        self.original_alpha = 255
        self.alpha = 255
    
    def update(self, dt, enemies=None):
        """Update animation and deal damage at the appropriate frame"""
        if self.finished:
            # If finished and in fade out state, process fade out
            if self.fading_out:
                self.fade_timer += dt
                # Calculate alpha based on fade timer
                self.alpha = max(0, int(self.original_alpha * (1 - (self.fade_timer / self.fade_duration))))
                
                # Create a copy of the image with the new alpha
                if self.image and hasattr(self.image, 'copy'):
                    temp_image = self.image.copy()
                    temp_image.set_alpha(self.alpha)
                    self.image = temp_image
                
                # Kill the sprite once fade is complete
                if self.alpha <= 0:
                    self.kill()
            return
            
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1
            
            if self.frame_index >= len(self.frames):
                # Start fade out instead of immediately finishing
                self.finished = True
                self.fading_out = True
                self.fade_timer = 0
                return
            
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.position)
            
            # Deal damage at specific frame (typically middle of animation)
            if not self.has_dealt_damage and self.frame_index == 2:  # 3rd frame (index 2)
                self.has_dealt_damage = True
                
                if enemies:
                    self.deal_damage(enemies)
    
    def deal_damage(self, enemies):
        """Deal damage to enemies within radius"""
        for enemy in enemies:
            # Skip if enemy is already dying
            if hasattr(enemy, 'is_dying') and enemy.is_dying:
                continue
                
            # Calculate distance to enemy
            dx = enemy.rect.centerx - self.position[0]
            dy = enemy.rect.centery - self.position[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Apply damage if enemy is within radius
            if distance <= self.radius:
                if hasattr(enemy, 'take_hit'):
                    enemy.take_hit(self.damage)


# Add this after the ThunderStrike class

class HealSkill(Skill):
    """Heal skill that restores player's health to full"""
    def __init__(self, sound_manager=None):
        super().__init__(sound_manager)
        self.name = "Heal"
        self.description = "Restore health to full"
        self.price = 750
        self.cooldown = 20.0  # 20 seconds cooldown (longer than thunder strike)
        
        # Load skill icon for UI
        self.icon_path = os.path.join("assets", "UI", "skill", "heal.png")
        self.icon = pygame.image.load(self.icon_path).convert_alpha() if os.path.exists(self.icon_path) else None
        
        # Healing animation frames
        self.frames = []
        for i in range(1, 6):  # Assuming you have similar frame structure as thunder
            path = os.path.join("assets", "skill", "heal", f"heal ({i}).png")
            if os.path.exists(path):
                frame = pygame.image.load(path).convert_alpha()
                self.frames.append(frame)
            else:
                # Create a placeholder if images don't exist
                placeholder = pygame.Surface((128, 128), pygame.SRCALPHA)
                placeholder.fill((0, 255, 0, 100))  # Green semi-transparent
                self.frames.append(placeholder)
        
        # Sound effect path
        self.sound_path = os.path.join("assets", "sound", "skill", "heal.ogg")
    
    def activate(self, player_pos, target_pos=None, enemies=None):
        """Activate heal skill to restore player's health"""
        player = player_pos  # In this case, player_pos is the player object itself
        
        # Play heal sound
        if self.sound_manager:
            self.sound_manager.play_skill_sound("heal")
        
        # Heal the player
        if hasattr(player, 'health') and hasattr(player, 'max_health'):
            player.health = player.max_health
        
        # Create and return the visual effect
        effect = HealEffect(player.rect.center, self.frames)
        return effect


class HealEffect(pygame.sprite.Sprite):
    """Visual effect for Heal skill"""
    def __init__(self, position, frames):
        super().__init__()
        self.position = position
        self.frames = frames
        
        # Animation properties
        self.frame_index = 0
        self.animation_speed = 0.1  # Time between frames in seconds
        self.animation_timer = 0
        self.image = self.frames[0] if self.frames else None
        
        if self.image:
            self.rect = self.image.get_rect(center=self.position)
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
        
        self.finished = False
        self.has_healed = False
        
        # Fade out properties
        self.fading_out = False
        self.fade_duration = 0.3  # Fade duration in seconds
        self.fade_timer = 0
        self.original_alpha = 255
        self.alpha = 255
    
    def update(self, dt, enemies=None):
        """Update animation and apply healing effect"""
        # Update position if player moves
        if hasattr(self, 'player') and self.player:
            self.position = self.player.rect.center
            self.rect.center = self.position
            
        if self.finished:
            # If finished and in fade out state, process fade out
            if self.fading_out:
                self.fade_timer += dt
                # Calculate alpha based on fade timer
                self.alpha = max(0, int(self.original_alpha * (1 - (self.fade_timer / self.fade_duration))))
                
                # Create a copy of the image with the new alpha
                if self.image and hasattr(self.image, 'copy'):
                    temp_image = self.image.copy()
                    temp_image.set_alpha(self.alpha)
                    self.image = temp_image
                
                # Kill the sprite once fade is complete
                if self.alpha <= 0:
                    self.kill()
            return
            
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.frame_index += 1
            
            if self.frame_index >= len(self.frames):
                # Start fade out instead of immediately finishing
                self.finished = True
                self.fading_out = True
                self.fade_timer = 0
                return
            
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(center=self.position)

# Add the Nuke skill class after the other skill classes
class NukeSkill(Skill):
    """Nuke skill that eliminates all enemies but damages the player"""
    def __init__(self, sound_manager=None):
        super().__init__(sound_manager)
        self.name = "Nuke"
        self.description = "Eliminate all enemies but costs 50% of your health"
        self.price = 1000
        self.cooldown = 60.0  # 60 seconds (1 minute) cooldown
        
        # Load skill icon for UI
        self.icon_path = os.path.join("assets", "UI", "skill", "nuke.png")
        self.icon = pygame.image.load(self.icon_path).convert_alpha() if os.path.exists(self.icon_path) else None
        
        # For the nuke effect, we'll use a white flash rather than animation frames
        self.flash_duration = 3.0  # Total flash effect duration in seconds
        self.fade_in_duration = 0.5  # Time to reach peak brightness
        self.hold_duration = 1.0  # Time to hold at peak brightness
        self.fade_out_duration = 1.5  # Time to fade back to normal
        
        # Sound effect path
        self.sound_path = os.path.join("assets", "sound", "skill", "nuke.ogg")
    
    def activate(self, player, target_pos=None, enemies=None):
        """
        Activate nuke skill to eliminate all enemies but damage the player
        
        Args:
            player: The player object
            target_pos: Ignored for this skill
            enemies: List of enemy objects to eliminate
        
        Returns:
            NukeEffect object for visual rendering
        """
        # Play nuke sound
        if self.sound_manager:
            self.sound_manager.play_skill_sound("nuke")
        
        # Deal 50% damage to player
        if hasattr(player, 'health') and hasattr(player, 'max_health'):
            damage = player.health * 0.5  # 50% of current health
            player.health -= damage
            
            # Check if player killed themselves with the nuke
            if player.health <= 0:
                player.health = 0
                if hasattr(player, 'start_death_animation'):
                    player.start_death_animation()
                else:
                    # Fallback if player doesn't have start_death_animation method
                    player.is_dying = True
        
        # Eliminate all enemies if provided
        killed_count = 0
        if enemies:
            for enemy in enemies:
                if hasattr(enemy, 'is_dying') and not enemy.is_dying:
                    if hasattr(enemy, 'take_hit'):
                        enemy.take_hit(99999)  # Instant kill with massive damage
                    else:
                        # Fallback if enemy doesn't have take_hit method
                        enemy.health = 0
                        enemy.is_dying = True
                    killed_count += 1
        
        # Create and return the visual effect
        effect = NukeEffect(self.flash_duration, self.fade_in_duration, 
                           self.hold_duration, self.fade_out_duration,
                           killed_count)
        return effect


class NukeEffect(pygame.sprite.Sprite):
    """Visual effect for Nuke skill - full screen white flash"""
    def __init__(self, duration, fade_in_duration, hold_duration, fade_out_duration, killed_count):
        super().__init__()
        self.duration = duration
        self.fade_in_duration = fade_in_duration
        self.hold_duration = hold_duration
        self.fade_out_duration = fade_out_duration
        self.killed_count = killed_count
        
        # Create a full-screen transparent white surface
        # Instead of using the display size, use a much larger size to cover the entire map
        self.screen_size = pygame.display.get_surface().get_size()
        self.image = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))  # Position at top-left
        
        # Animation properties
        self.timer = 0
        self.finished = False
        self.block_spawns_duration = 5.0  # Block enemy spawns for 5 seconds
        self.block_spawns_timer = 0
        
        # Alpha values for fading
        self.alpha = 0
        
        # Set a flag that can be checked by the game loop to prevent enemy spawning
        self.block_enemy_spawns = True
        
        # Fill initially with transparent white
        self.image.fill((255, 255, 255, self.alpha))
        
        # Extra flag to indicate this is a full-screen effect (not tied to camera)
        self.is_fullscreen_effect = True
    
    def update(self, dt, enemies=None):
        """Update the flash effect and spawn blocking timer"""
        # Update the spawn blocking timer
        if self.block_enemy_spawns:
            self.block_spawns_timer += dt
            if self.block_spawns_timer >= self.block_spawns_duration:
                self.block_enemy_spawns = False
        
        # Update the flash effect timer
        self.timer += dt
        
        # Calculate the current phase of the effect
        if self.timer < self.fade_in_duration:
            # Fade in phase
            progress = self.timer / self.fade_in_duration
            self.alpha = int(255 * progress)
        elif self.timer < self.fade_in_duration + self.hold_duration:
            # Hold at full brightness
            self.alpha = 255
        elif self.timer < self.duration:
            # Fade out phase
            fade_out_progress = (self.timer - (self.fade_in_duration + self.hold_duration)) / self.fade_out_duration
            self.alpha = int(255 * (1 - fade_out_progress))
        else:
            # Effect complete
            self.alpha = 0
            self.finished = True
            # Don't kill the sprite yet - we need to keep it alive until spawn block is over
            if not self.block_enemy_spawns:
                self.kill()
            return
        
        # Update the surface with new alpha
        self.image.fill((255, 255, 255, self.alpha))
    
    def draw(self, surface, camera_offset=None):
        """Custom draw method to draw directly on screen instead of using camera offset"""
        # For a full-screen effect, we want to draw on the surface directly
        # Ignore camera offset completely
        surface.blit(self.image, (0, 0))

SKILL_REGISTRY = {
    "thunder_strike": ThunderStrike,
    "heal": HealSkill,
    "nuke": NukeSkill
}

def create_skill(skill_name, sound_manager=None):
    """Factory function to create a skill by name"""
    if skill_name in SKILL_REGISTRY:
        skill = SKILL_REGISTRY[skill_name](sound_manager)
        
        # Load icon if it doesn't exist
        if not hasattr(skill, 'icon') or skill.icon is None:
            icon_path = os.path.join("assets", "UI", "skill", f"{skill_name}.png")
            if os.path.exists(icon_path):
                skill.icon = pygame.image.load(icon_path).convert_alpha()
                skill.icon_path = icon_path
        return skill
    return None