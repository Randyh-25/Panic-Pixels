import pygame
import random
import math
import os

class Map:
    def __init__(self, map_file):
        # Check if file exists
        if not os.path.exists(map_file):
            raise FileNotFoundError(f"Map file not found: {map_file}")
            
        try:
            # Load the base map image with alpha channel
            self.base_map = pygame.image.load(map_file).convert_alpha()
        except pygame.error as e:
            raise Exception(f"Could not load map image: {e}")
            
        # Create a background color surface
        self.bg_color = (245, 222, 179)  # Sand/desert color
        
        # Calculate dimensions for 4x4 grid of maps
        self.tile_width = self.base_map.get_width()
        self.tile_height = self.base_map.get_height()
        self.width = self.tile_width * 4
        self.height = self.tile_height * 4
        
        # Create the full map surface
        self.map_surface = pygame.Surface((self.width, self.height))
        self.map_surface.fill(self.bg_color)
        
        # Fill the 4x4 grid with map tiles
        for row in range(4):
            for col in range(4):
                self.map_surface.blit(
                    self.base_map,
                    (col * self.tile_width, row * self.tile_height)
                )
        
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

        # Add collision rectangles list for dead trees
        self.tree_collision_rects = []
        
        # Load natural objects with correct filenames
        self.object_scales = {
            'bush': 1.2,    # Changed from bush1
            'bush2': 1.2,
            'bush3': 1.2,
            'cactus': 1.5,
            'dead-tree': 1.8,
            'dead-tree2': 1.8,
            'dead-tree3': 1.8,
            'dead-tree4': 1.8,
            'dead-tree5': 1.8
        }
        
        # Load and scale objects with proper error handling
        self.natural_objects = {}
        for key, scale in self.object_scales.items():
            try:
                path = f"assets/maps/desert/obj/{key}.png"
                if not os.path.exists(path):
                    print(f"Warning: {path} not found, skipping...")
                    continue
                    
                img = pygame.image.load(path).convert_alpha()
                size = (int(img.get_width() * scale), int(img.get_height() * scale))
                self.natural_objects[key] = pygame.transform.scale(img, size)
            except Exception as e:
                print(f"Error loading {key}: {e}")
                continue

        # Generate natural objects after creating map surface but before fences
        self._generate_natural_objects()

    def _create_shadow(self, surface, blur_radius=3, offset=(4, 4), shadow_color=(20, 20, 20)):
        # Create shadow surface with alpha
        shadow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Create mask from original surface
        mask = pygame.mask.from_surface(surface)
        mask_surface = mask.to_surface(setcolor=shadow_color + (100,))  # Semi-transparent shadow
        
        # Apply simple blur effect
        for _ in range(blur_radius):
            temp = mask_surface.copy()
            for x in range(1, mask_surface.get_width()-1):
                for y in range(1, mask_surface.get_height()-1):
                    # Average of surrounding pixels
                    colors = []
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        colors.append(temp.get_at((x+dx, y+dy)))
                    avg_color = [sum(c)/len(colors) for c in zip(*colors)]
                    mask_surface.set_at((x, y), avg_color)
        
        return mask_surface

    def _generate_natural_objects(self):
        # Create environmental zones
        zones = self._create_environmental_zones()
        
        # Define safe margins from fences
        margin = 60
        safe_area = pygame.Rect(margin, margin, self.width - 2 * margin, self.height - 2 * margin)
        
        # Clear previous tree collision rects
        self.tree_collision_rects = []
        
        # Generate objects based on zones
        for zone in zones:
            center_x, center_y = zone['center']
            radius = zone['radius']
            zone_type = zone['type']
            
            # Reduce number of objects
            if zone_type == 'dense':
                num_objects = random.randint(8, 12)
                tree_chance = 0.15  # Reduce tree chance
            elif zone_type == 'scattered':
                num_objects = random.randint(4, 8)
                tree_chance = 0.1
            else:  # sparse
                num_objects = random.randint(2, 5)
                tree_chance = 0.05
            
            for _ in range(num_objects):
                # Use polar coordinates for distribution
                angle = random.uniform(0, 2 * math.pi)
                distance = math.sqrt(random.uniform(0, 1)) * radius
                
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                
                if not safe_area.collidepoint(x, y):
                    continue
                
                # Determine object type
                if random.random() < tree_chance:
                    object_type = random.choice(['dead-tree', 'dead-tree2', 'dead-tree3', 
                                       'dead-tree4', 'dead-tree5'])
                    scale = 1.0
                else:
                    object_type = random.choices(
                        ['bush', 'bush2', 'bush3', 'cactus'],  # Updated bush name
                        weights=[15, 15, 15, 10],
                        k=1
                    )[0]
                    scale = random.uniform(0.9, 1.1)  # Slight scale variation for bushes
                
                # Get and scale object
                obj = self.natural_objects[object_type]
                if object_type not in ['dead-tree', 'dead-tree2', 'dead-tree3', 'dead-tree4', 'dead-tree5']:
                    size = (int(obj.get_width() * scale), int(obj.get_height() * scale))
                    obj = pygame.transform.scale(obj, size)
                
                # Position object
                pos_x = int(x - obj.get_width() // 2)
                pos_y = int(y - obj.get_height() // 2)
                
                # Add collision rect for trees
                if 'tree' in object_type:
                    # Make collision rect slightly smaller than visual tree
                    collision_shrink = 0.7  # 70% of original size
                    rect_width = int(obj.get_width() * collision_shrink)
                    rect_height = int(obj.get_height() * collision_shrink)
                    rect_x = pos_x + (obj.get_width() - rect_width) // 2
                    rect_y = pos_y + (obj.get_height() - rect_height) // 2
                    
                    tree_rect = pygame.Rect(rect_x, rect_y, rect_width, rect_height)
                    self.tree_collision_rects.append(tree_rect)
                
                # Draw object
                self.map_surface.blit(obj, (pos_x, pos_y))

    def _create_environmental_zones(self):
        zones = []
        
        # Create larger zones first
        for _ in range(3):
            center_x = random.randint(100, self.width - 100)
            center_y = random.randint(100, self.height - 100)
            radius = random.randint(400, 600)
            zones.append({
                'center': (center_x, center_y),
                'radius': radius,
                'type': 'dense'
            })
        
        # Add medium scattered zones
        for _ in range(4):
            center_x = random.randint(100, self.width - 100)
            center_y = random.randint(100, self.height - 100)
            radius = random.randint(200, 400)
            zones.append({
                'center': (center_x, center_y),
                'radius': radius,
                'type': 'scattered'
            })
        
        # Add small sparse zones
        for _ in range(6):
            center_x = random.randint(100, self.width - 100)
            center_y = random.randint(100, self.height - 100)
            radius = random.randint(100, 200)
            zones.append({
                'center': (center_x, center_y),
                'radius': radius,
                'type': 'sparse'
            })
        
        return zones

    def draw(self, screen, camera):
        screen.blit(self.map_surface, (camera.x, camera.y))