import pygame
import random
import math

class DustParticle:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x # posisi horizontal awal 
        self.y = y # posisi vertikel awal
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = random.uniform(2, 5) 
        self.speed = random.uniform(0.2, 1.0) 
        self.angle = random.uniform(0, 2 * math.pi) # arah gerak partikel dalam radian
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.max_lifetime = random.randint(200, 500) # waktu hidup maksimum partikel
        self.lifetime = self.max_lifetime # sisa waktu hidup partikel, dan akan menurun tiap frame
        self.alpha = random.randint(50, 150) # transparansi partikel
        
        base_colors = [
            (245, 222, 179),  # Light sand
            (210, 180, 140),  # Tan
            (255, 228, 181),  # Moccasin
        ]
        base_color = random.choice(base_colors)
        variation = random.randint(-10, 10)
        self.color = tuple(max(0, min(255, c + variation)) for c in base_color)

class ParticleSystem:
    def __init__(self, screen_width, screen_height):
        self.particles = [] # list untuk menyimpan semua partikel yang aktif
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.particle_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.max_particles = 50  # batasi jumlah maksimum partikel 
        
    def create_particle(self, x, y):
        if len(self.particles) < self.max_particles: # hanya menambahkan jika belum mencapai batas maksimum
            self.particles.append(DustParticle(x, y, self.screen_width, self.screen_height))
            
    def update(self, camera_x, camera_y):
        # update hanya partikel yang terlihat dilayar
        screen_rect = pygame.Rect(-camera_x, -camera_y, self.screen_width, self.screen_height)
        
        for particle in self.particles[:]:
            if screen_rect.collidepoint(particle.x, particle.y): # hanya update partikel yang terlihat
                particle.x += particle.dx
                particle.y += particle.dy
                particle.lifetime -= 1 # kurangi umur partikel setiap frame
                
                if particle.lifetime <= 0: # jika umur habis
                    self.particles.remove(particle) # hapus partikel dari sistem
                else:
                    particle.alpha = int((particle.lifetime / particle.max_lifetime) * 100)

            # wrap-around (membuat partikel muncul kembali ke sisi lain layar jika keluar dari batas)
            particle.x = (particle.x + self.screen_width) % self.screen_width
            particle.y = (particle.y + self.screen_height) % self.screen_height
            
    def draw(self, screen, camera):
        self.particle_surface.fill((0, 0, 0, 0))
    
        for particle in self.particles:
            screen_x = (particle.x + camera.x) % self.screen_width
            screen_y = (particle.y + camera.y) % self.screen_height
            
            particle_surf = pygame.Surface((int(particle.size), int(particle.size)), pygame.SRCALPHA)
            
            particle_color = particle.color + (particle.alpha,)
            particle_surf.fill(particle_color)
            
            self.particle_surface.blit(particle_surf, (screen_x, screen_y))
        
        screen.blit(self.particle_surface, (0, 0))
