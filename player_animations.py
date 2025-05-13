import pygame
import os

class PlayerAnimations:
    def __init__(self):
        self.animations = {
            'idle_down': [], 'walk_down': [],
            'idle_down_right': [], 'walk_down_right': [],
            'idle_down_left': [], 'walk_down_left': [],
            'idle_right': [], 'walk_right': [],
            'idle_left': [], 'walk_left': [],
            'idle_up': [], 'walk_up': [],
            'idle_up_right': [], 'walk_up_right': [],
            'idle_up_left': [], 'walk_up_left': [],
            'death': []
        }
        
        self.animation_config = {
            'idle_down': {'count': 6, 'prefix': 'idle', 'dir': 'down'},
            'walk_down': {'count': 8, 'prefix': 'walk', 'dir': 'down'},
            'idle_down_right': {'count': 6, 'prefix': 'idle', 'dir': 'down-right'},
            'walk_down_right': {'count': 8, 'prefix': 'walk', 'dir': 'down-right'},
            'idle_right': {'count': 6, 'prefix': 'idle', 'dir': 'right'},
            'walk_right': {'count': 8, 'prefix': 'walk', 'dir': 'right'},
            'idle_up': {'count': 6, 'prefix': 'idle', 'dir': 'up'},
            'walk_up': {'count': 8, 'prefix': 'walk', 'dir': 'up'},
            'idle_up_right': {'count': 6, 'prefix': 'idle', 'dir': 'up-right'},
            'walk_up_right': {'count': 8, 'prefix': 'walk', 'dir': 'up-right'},
            'death': {'count': 14, 'prefix': 'death', 'dir': 'death'}
        }
        
        for anim_name, config in self.animation_config.items():
            directory = config['dir']
            
            if anim_name == 'death':
                for i in range(1, config['count'] + 1):
                    image_path = os.path.join('assets', 'player', 'cowboy', 'death', 
                                            f"{config['prefix']} ({i}).png")
                    try:
                        image = pygame.image.load(image_path).convert_alpha()
                        image = pygame.transform.scale(image, (64, 64))
                        self.animations['death'].append(image)
                    except pygame.error as e:
                        print(f"Couldn't load death animation: {image_path}")
                        print(e)
                continue
                
            for i in range(1, config['count'] + 1):
                image_path = os.path.join('assets', 'player', 'cowboy', directory, 
                                        f"{config['prefix']} ({i}).png")
                try:
                    image = pygame.image.load(image_path).convert_alpha()
                    image = pygame.transform.scale(image, (64, 64))
                
                    self.animations[anim_name].append(image)
                    
                    if any(direction in anim_name for direction in ['right', 'down_right', 'up_right']):
                        left_anim_name = anim_name.replace('right', 'left')
                        flipped = pygame.transform.flip(image, True, False)
                        self.animations[left_anim_name].append(flipped)
                        
                except pygame.error as e:
                    print(f"Couldn't load image: {image_path}")
                    print(e)
                    continue
        
        self.current_animation = 'idle_down'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0