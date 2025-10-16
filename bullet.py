import pygame
import random
import math

class Bullet:
    def __init__(self, x, y, vx, vy, font=None, sound_manager=None):
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(vx, vy)
        self.radius = 6  # Much smaller
        self.lifespan = 60
        self.symbol = "AIC"
        self.rect = pygame.Rect(0, 0, self.radius * 4, self.radius * 2)
        self.update_rect()
        self.sound_manager = sound_manager
        self.font = font if font else pygame.font.SysFont("Arial Black", 12, bold=True)  # Smaller font

        # Laser effect parameters
        self.glow_alpha = 150
        self.glow_growing = True
        self.glow_pulse_speed = 6
        self.trail_particles = []

    def update_rect(self):
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self):
        self.pos += self.vel
        self.lifespan -= 1
        self.animate_glow()
        
        # Create small trail effect
        if random.random() < 0.3:
            self.trail_particles.append({
                'pos': self.pos.copy(),
                'age': 0,
                'max_age': 12
            })
        
        # Update trail particles
        for particle in self.trail_particles[:]:
            particle['age'] += 1
            if particle['age'] >= particle['max_age']:
                self.trail_particles.remove(particle)
        
        self.update_rect()

    def animate_glow(self):
        if self.glow_growing:
            self.glow_alpha += self.glow_pulse_speed
            if self.glow_alpha >= 200:
                self.glow_alpha = 200
                self.glow_growing = False
        else:
            self.glow_alpha -= self.glow_pulse_speed
            if self.glow_alpha <= 100:
                self.glow_alpha = 100
                self.glow_growing = True

    def draw(self, screen):
        # Draw small trail particles
        for particle in self.trail_particles:
            alpha = int(180 * (1 - particle['age'] / particle['max_age']))
            color = (255, 255, 0, alpha)
            trail_size = 3
            trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, color, (trail_size, trail_size), trail_size)
            screen.blit(trail_surf, (particle['pos'].x - trail_size, particle['pos'].y - trail_size), 
                       special_flags=pygame.BLEND_ADD)

        # Draw compact glow
        glow_radius = self.radius * 2.5
        glow_alpha = int(self.glow_alpha)
        glow_color = (255,0, 0, glow_alpha)
        glow_size = int(glow_radius)
        glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, glow_color, (glow_size, glow_size), glow_size)
        screen.blit(glow_surface,
                   (self.pos.x - glow_size, self.pos.y - glow_size),
                   special_flags=pygame.BLEND_ADD)

        # Draw tiny 'AIC' text
        letter_surface = self.font.render(self.symbol, True, (200, 255, 255))
        rect = letter_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        screen.blit(letter_surface, rect)
        
        # Core bright dot
        pygame.draw.circle(screen, (255, 255, 255), (int(self.pos.x), int(self.pos.y)), 2)
        pygame.draw.circle(screen, (0, 255, 255), (int(self.pos.x), int(self.pos.y)), 4, 1)
