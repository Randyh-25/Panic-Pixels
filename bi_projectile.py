import pygame
import math

class BiProjectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos, image):
        super().__init__()
        # Reduce the size of the sting projectile
        self.original_image = image
        scaled_size = (8, 8)  # Smaller sting size
        self.original_image = pygame.transform.scale(self.original_image, scaled_size)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        
        # Calculate direction and velocity
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        
        self.speed = 5.0  # Projectile speed
        
        if dist > 0:
            self.velocity = pygame.math.Vector2(
                dx / dist * self.speed,
                dy / dist * self.speed
            )
        else:
            self.velocity = pygame.math.Vector2(0, -self.speed)
        
        # Rotate the sting to point in the direction of travel
        # The angle calculation ensures the pointy end points toward the target
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.original_image, angle - 90)  # -90 to adjust for image orientation
        self.rect = self.image.get_rect(center=self.pos)
        
        # Damage for the projectile
        self.damage = 8
        
        # Lifetime to ensure projectiles don't fly forever
        self.lifetime = 180  # frames (at 60 fps = ~3 seconds)
        self.age = 0

    def update(self):
        # Move the projectile
        self.pos += self.velocity
        self.rect.center = self.pos
        
        # Age the projectile
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()