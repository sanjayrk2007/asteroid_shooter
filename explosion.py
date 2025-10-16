import pygame
import random
import math

class Particle:
    def __init__(self, x, y, explosion_type='normal'):
        self.pos = pygame.Vector2(x, y)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5) if explosion_type == 'normal' else random.uniform(2, 7)
        self.vel = pygame.Vector2(speed * math.cos(angle), speed * math.sin(angle))
        self.lifespan = random.randint(30, 60)
        self.radius = random.randint(2, 6)
        
        # Color variation based on explosion type
        if explosion_type == 'asteroid':
            self.color = pygame.Color(random.randint(200, 255), 
                                     random.randint(100, 150), 0)
        else:
            self.color = pygame.Color(random.randint(150, 255), 
                                     random.randint(50, 150), 
                                     random.randint(0, 100))
        self.age = 0
        self.explosion_type = explosion_type

    def update(self):
        self.pos += self.vel
        self.age += 1
        self.vel *= 0.92
        self.color.a = max(0, 255 - (255 * self.age // self.lifespan))
        
        if self.age > self.lifespan // 2:
            self.radius = max(1, self.radius - 0.1)

    def draw(self, screen):
        if self.color.a > 0:
            glow_surf = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            glow_color = (*self.color[:3], self.color.a // 3)
            pygame.draw.circle(glow_surf, glow_color, 
                             (self.radius * 2, self.radius * 2), self.radius * 2)
            screen.blit(glow_surf, (self.pos.x - self.radius * 2, 
                                   self.pos.y - self.radius * 2),
                       special_flags=pygame.BLEND_ADD)
            
            particle_surf = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), 
                                          pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, self.color, 
                             (int(self.radius), int(self.radius)), int(self.radius))
            screen.blit(particle_surf, (self.pos.x - self.radius, 
                                       self.pos.y - self.radius))


class ExplosionManager:
    def __init__(self):
        self.particles = []

    def create_explosion(self, pos, size, explosion_type='normal'):
        count = size * 5
        for _ in range(count):
            self.particles.append(Particle(pos.x, pos.y, explosion_type))
        
        if size > 20:
            for _ in range(10):
                self.particles.append(Particle(pos.x, pos.y, 'shockwave'))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if p.age >= p.lifespan:
                self.particles.remove(p)

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
