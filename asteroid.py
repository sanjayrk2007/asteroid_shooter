import pygame
import random
import math

class Asteroid:
    def __init__(self, x, y, size):
        self.pos = pygame.Vector2(x, y)
        self.size = size
        self.radius = {3: 40, 2: 25, 1: 15}[size]
        self.speed = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        self.angle = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.vertices_count = random.randint(8, 14)
        self.offsets = [random.uniform(0.7, 1.3) for _ in range(self.vertices_count)]
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.update_rect()
        self.point_value = {3: 20, 2: 50, 1: 100}[size]
        
        # Advanced visual features
        self.inner_detail_points = []
        self.generate_inner_details()
        self.color_variation = random.randint(-30, 30)
        self.glow_pulse = random.uniform(0, 360)

    def generate_inner_details(self):
        """Generate crater-like details inside asteroid"""
        crater_count = random.randint(2, 5)
        for _ in range(crater_count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, self.radius * 0.5)
            crater_size = random.randint(2, 5)
            self.inner_detail_points.append({
                'angle': angle,
                'distance': distance,
                'size': crater_size
            })

    def update_rect(self):
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self):
        self.pos += self.speed
        self.angle = (self.angle + self.rotation_speed) % 360
        self.glow_pulse = (self.glow_pulse + 2) % 360
        
        screen_width, screen_height = pygame.display.get_surface().get_size()
        if self.pos.x < -self.radius:
            self.pos.x = screen_width + self.radius
        elif self.pos.x > screen_width + self.radius:
            self.pos.x = -self.radius
        if self.pos.y < -self.radius:
            self.pos.y = screen_height + self.radius
        elif self.pos.y > screen_height + self.radius:
            self.pos.y = -self.radius
        self.update_rect()

    def draw(self, screen):
        # Calculate outer polygon points
        points = []
        angle_between_vertices = 2 * math.pi / self.vertices_count
        for i in range(self.vertices_count):
            angle_vertex = angle_between_vertices * i + math.radians(self.angle)
            rad = self.radius * self.offsets[i]
            x = self.pos.x + rad * math.cos(angle_vertex)
            y = self.pos.y + rad * math.sin(angle_vertex)
            points.append((x, y))
        
        # Draw subtle glow effect
        glow_intensity = 20 + int(10 * math.sin(math.radians(self.glow_pulse)))
        glow_color = (150 + glow_intensity, 150 + glow_intensity, 150 + glow_intensity)
        glow_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*glow_color, 30), 
                          (int(self.radius * 1.5), int(self.radius * 1.5)), 
                          int(self.radius * 1.2))
        screen.blit(glow_surface, 
                   (self.pos.x - self.radius * 1.5, self.pos.y - self.radius * 1.5),
                   special_flags=pygame.BLEND_ADD)
        
        # Draw filled polygon with color variation
        base_color = 180 + self.color_variation
        fill_color = (base_color, base_color, base_color)
        pygame.draw.polygon(screen, fill_color, points)
        
        # Draw outline with slight color gradient
        outline_color = (220, 220, 220)
        pygame.draw.polygon(screen, outline_color, points, 3)
        
        # Draw inner crater details
        for detail in self.inner_detail_points:
            detail_angle = detail['angle'] + math.radians(self.angle)
            detail_x = self.pos.x + detail['distance'] * math.cos(detail_angle)
            detail_y = self.pos.y + detail['distance'] * math.sin(detail_angle)
            pygame.draw.circle(screen, (100, 100, 100), 
                             (int(detail_x), int(detail_y)), detail['size'])
            pygame.draw.circle(screen, (140, 140, 140), 
                             (int(detail_x), int(detail_y)), detail['size'], 1)


class AsteroidManager:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.asteroids = []
        self.spawn_timer = 0
        self.spawn_interval = 180

    def spawn_initial(self, count=5):
        self.asteroids.clear()
        for _ in range(count):
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                x, y = -50, random.uniform(0, self.screen_height)
            elif side == 'right':
                x, y = self.screen_width + 50, random.uniform(0, self.screen_height)
            elif side == 'top':
                x, y = random.uniform(0, self.screen_width), -50
            else:
                x, y = random.uniform(0, self.screen_width), self.screen_height + 50
            self.asteroids.append(Asteroid(x, y, 3))

    def update(self):
        for asteroid in self.asteroids:
            asteroid.update()
        
        # Spawn new asteroids periodically
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval and len(self.asteroids) < 15:
            self.spawn_timer = 0
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                x, y = -50, random.uniform(0, self.screen_height)
            elif side == 'right':
                x, y = self.screen_width + 50, random.uniform(0, self.screen_height)
            elif side == 'top':
                x, y = random.uniform(0, self.screen_width), -50
            else:
                x, y = random.uniform(0, self.screen_width), self.screen_height + 50
            self.asteroids.append(Asteroid(x, y, random.choice([3, 2])))

    def draw(self, screen):
        for asteroid in self.asteroids:
            asteroid.draw(screen)

    def destroy(self, asteroid):
        if asteroid.size > 1:
            for _ in range(2):
                new_size = asteroid.size - 1
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                new_asteroid = Asteroid(asteroid.pos.x + offset_x, 
                                      asteroid.pos.y + offset_y, new_size)
                self.asteroids.append(new_asteroid)
        if asteroid in self.asteroids:
            self.asteroids.remove(asteroid)
