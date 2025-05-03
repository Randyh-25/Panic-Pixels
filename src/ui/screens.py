import pygame

class MainMenu:
    def __init__(self):
        self.title_font = pygame.font.SysFont('Arial', 48)
        self.option_font = pygame.font.SysFont('Arial', 36)
        self.options = ['Start Game', 'Options', 'Quit']
        self.selected_option = 0

    def draw(self, screen):
        screen.fill((0, 0, 0))
        title_surface = self.title_font.render('Arcade Game', True, (255, 255, 255))
        screen.blit(title_surface, (screen.get_width() // 2 - title_surface.get_width() // 2, 100))

        for index, option in enumerate(self.options):
            color = (255, 255, 0) if index == self.selected_option else (255, 255, 255)
            option_surface = self.option_font.render(option, True, color)
            screen.blit(option_surface, (screen.get_width() // 2 - option_surface.get_width() // 2, 200 + index * 50))

    def move_selection(self, direction):
        self.selected_option = (self.selected_option + direction) % len(self.options)

class GameOverScreen:
    def __init__(self, score):
        self.score = score
        self.font = pygame.font.SysFont('Arial', 36)

    def draw(self, screen):
        screen.fill((0, 0, 0))
        game_over_surface = self.font.render('Game Over', True, (255, 0, 0))
        score_surface = self.font.render(f'Your Score: {self.score}', True, (255, 255, 255))
        screen.blit(game_over_surface, (screen.get_width() // 2 - game_over_surface.get_width() // 2, 100))
        screen.blit(score_surface, (screen.get_width() // 2 - score_surface.get_width() // 2, 200))