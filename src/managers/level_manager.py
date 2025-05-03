import pygame
import os

class LevelManager:
    def __init__(self):
        self.current_level = 0
        self.levels = []
        self.load_levels()

    def load_levels(self):
        # Load levels from a predefined directory or file
        level_directory = os.path.join("assets", "levels")
        for level_file in os.listdir(level_directory):
            if level_file.endswith(".json"):  # Assuming levels are stored in JSON format
                self.levels.append(os.path.join(level_directory, level_file))

    def get_current_level(self):
        if self.current_level < len(self.levels):
            return self.levels[self.current_level]
        return None

    def next_level(self):
        if self.current_level < len(self.levels) - 1:
            self.current_level += 1
            return self.get_current_level()
        return None

    def reset_levels(self):
        self.current_level = 0

    def is_last_level(self):
        return self.current_level >= len(self.levels) - 1