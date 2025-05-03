import pygame

class HUD:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, screen):
        health_text = self.font.render(f"Health: {self.player.health}", True, (255, 255, 255))
        score_text = self.font.render(f"Score: {self.player.score}", True, (255, 255, 255))
        screen.blit(health_text, (10, 10))
        screen.blit(score_text, (10, 50))