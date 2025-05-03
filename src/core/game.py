import pygame
import sys
from src.core.settings import WIDTH, HEIGHT, FPS, BLACK
from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.projectile import Projectile
from src.managers.audio_manager import AudioManager
from src.managers.level_manager import LevelManager
from src.ui.hud import HUD

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Arcade Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.hud = HUD(self.player)
        
        self.audio_manager = AudioManager()
        self.level_manager = LevelManager()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.player.update()
        self.enemies.update(self.player)
        self.projectiles.update()
        self.check_collisions()

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)
        self.enemies.draw(self.screen)
        self.projectiles.draw(self.screen)
        self.hud.draw(self.screen)
        pygame.display.flip()

    def check_collisions(self):
        # Implement collision detection logic here
        pass

if __name__ == "__main__":
    game = Game()
    game.run()