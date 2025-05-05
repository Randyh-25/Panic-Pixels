import pygame

class Map:
    def __init__(self, map_file):
        # Load the base map image
        self.base_map = pygame.image.load(map_file).convert()
        
        # Load and scale fence assets
        scale_factor = 2  # Increase fence size
        
        # Load and scale vertical and horizontal fences
        self.fence_vertical = pygame.image.load("assets/maps/desert/obj/fence.png").convert_alpha()
        self.fence_horizontal = pygame.image.load("assets/maps/desert/obj/fence-horizontal.png").convert_alpha()
        
        # Scale fences
        vertical_size = (int(self.fence_vertical.get_width() * scale_factor), 
                       int(self.fence_vertical.get_height() * scale_factor))
        horizontal_size = (int(self.fence_horizontal.get_width() * scale_factor), 
                         int(self.fence_horizontal.get_height() * scale_factor))
        
        self.fence_vertical = pygame.transform.scale(self.fence_vertical, vertical_size)
        self.fence_horizontal = pygame.transform.scale(self.fence_horizontal, horizontal_size)
        
        # Load and scale corner fences with correct filenames
        self.fence_corners = {}
        corner_files = {
            'tl': 'fence-border-top-left.png',
            'tr': 'fence-border-top-right.png',
            'bl': 'fence-border-bottom-left.png',
            'br': 'fence-border-bottom-right.png'
        }
        
        for key, filename in corner_files.items():
            img = pygame.image.load(f"assets/maps/desert/obj/{filename}").convert_alpha()
            size = (int(img.get_width() * scale_factor), 
                   int(img.get_height() * scale_factor))
            self.fence_corners[key] = pygame.transform.scale(img, size)
        
        # Calculate dimensions for 4x4 grid of maps
        self.tile_width = self.base_map.get_width()
        self.tile_height = self.base_map.get_height()
        self.width = self.tile_width * 4
        self.height = self.tile_height * 4
        
        # Create the full map surface
        self.map_surface = pygame.Surface((self.width, self.height))
        
        # Fill the 4x4 grid with map tiles
        for row in range(4):
            for col in range(4):
                self.map_surface.blit(
                    self.base_map,
                    (col * self.tile_width, row * self.tile_height)
                )
        
        # Create fence collision group
        self.fence_rects = []
        
        # Add corner fences with offset
        offset = 10  # Adjust fence position from edge
        
        # Add corners and their collision rects
        corner_positions = [
            ('tl', (offset, offset)),
            ('tr', (self.width - self.fence_corners['tr'].get_width() - offset, offset)),
            ('bl', (offset, self.height - self.fence_corners['bl'].get_height() - offset)),
            ('br', (self.width - self.fence_corners['br'].get_width() - offset, 
                   self.height - self.fence_corners['br'].get_height() - offset))
        ]
        
        for corner, pos in corner_positions:
            self.map_surface.blit(self.fence_corners[corner], pos)
            self.fence_rects.append(pygame.Rect(
                pos[0], pos[1],
                self.fence_corners[corner].get_width(),
                self.fence_corners[corner].get_height()
            ))
        
        # Add straight fences
        h_spacing = self.fence_horizontal.get_width() - 5  # Spacing for horizontal fences
        v_spacing = self.fence_vertical.get_height() - 5   # Spacing for vertical fences
        
        # Add horizontal fences and their collision rects
        for x in range(offset + self.fence_corners['tl'].get_width(), 
                      self.width - self.fence_corners['tr'].get_width() - offset, 
                      h_spacing):
            # Top edge
            self.map_surface.blit(self.fence_horizontal, (x, offset))
            self.fence_rects.append(pygame.Rect(
                x, offset,
                self.fence_horizontal.get_width(),
                self.fence_horizontal.get_height()
            ))
            
            # Bottom edge
            bottom_y = self.height - self.fence_horizontal.get_height() - offset
            self.map_surface.blit(self.fence_horizontal, (x, bottom_y))
            self.fence_rects.append(pygame.Rect(
                x, bottom_y,
                self.fence_horizontal.get_width(),
                self.fence_horizontal.get_height()
            ))
        
        # Add vertical fences and their collision rects
        for y in range(offset + self.fence_corners['tl'].get_height(), 
                      self.height - self.fence_corners['bl'].get_height() - offset, 
                      v_spacing):
            # Left edge
            self.map_surface.blit(self.fence_vertical, (offset, y))
            self.fence_rects.append(pygame.Rect(
                offset, y,
                self.fence_vertical.get_width(),
                self.fence_vertical.get_height()
            ))
            
            # Right edge
            right_x = self.width - self.fence_vertical.get_width() - offset
            self.map_surface.blit(self.fence_vertical, (right_x, y))
            self.fence_rects.append(pygame.Rect(
                right_x, y,
                self.fence_vertical.get_width(),
                self.fence_vertical.get_height()
            ))

    def draw(self, screen, camera):
        screen.blit(self.map_surface, (camera.x, camera.y))