import pygame
import math
import random
import time

class Player:
    def __init__(self, x, y, sound_manager=None):
        self.pos = pygame.Vector2(x, y)
        self.radius = 20
        self.angle = 0
        self.speed = pygame.Vector2(0, 0)
        self.max_speed = 5
        self.acceleration = 0.2
        self.friction = 0.98
        self.rotating_left = False
        self.rotating_right = False
        self.thrusting = False
        self.shooting = False
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 15
        self.respawn_pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.update_rect()
        self.sound_manager = sound_manager
        self.thrust_start_time = None
        self.thrust_particles = []

    def update_rect(self):
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def update(self):
        if self.rotating_left:
            self.angle += 4
        if self.rotating_right:
            self.angle -= 4
        self.angle %= 360

        if self.thrusting:
            rad = math.radians(self.angle)
            force_x = math.cos(rad) * self.acceleration
            force_y = -math.sin(rad) * self.acceleration
            self.speed.x += force_x
            self.speed.y += force_y
            if self.sound_manager and self.thrust_start_time is None:
                self.sound_manager('thrust')
                self.thrust_start_time = time.time()

            # Spawn thrust particles
            for _ in range(3):
                offset_angle = self.angle + 180 + random.uniform(-20, 20)
                speed_p = random.uniform(2, 4)
                dx = math.cos(math.radians(offset_angle)) * speed_p
                dy = -math.sin(math.radians(offset_angle)) * speed_p
                particle_pos = pygame.Vector2(
                    self.pos.x - math.cos(rad) * self.radius * 1.2,
                    self.pos.y + math.sin(rad) * self.radius * 1.2
                )
                self.thrust_particles.append({
                    'pos': particle_pos,
                    'vel': pygame.Vector2(dx, dy),
                    'age': 0,
                    'max_age': random.randint(15, 25)
                })
        else:
            self.thrust_start_time = None

        self.speed *= self.friction
        if self.speed.length() > self.max_speed:
            self.speed.scale_to_length(self.max_speed)
        self.pos += self.speed

        screen_width, screen_height = pygame.display.get_surface().get_size()
        if self.pos.x < 0:
            self.pos.x = screen_width
        elif self.pos.x > screen_width:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = screen_height
        elif self.pos.y > screen_height:
            self.pos.y = 0
        self.update_rect()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update thrust particles
        for particle in self.thrust_particles[:]:
            particle['pos'] += particle['vel']
            particle['age'] += 1
            if particle['age'] >= particle['max_age']:
                self.thrust_particles.remove(particle)

    def shoot(self):
        if self.shoot_cooldown == 0:
            rad = math.radians(self.angle)
            bullet_vel = pygame.Vector2(math.cos(rad), -math.sin(rad)) * 10
            bullet_pos = self.pos + bullet_vel.normalize() * (self.radius + 10)
            self.shoot_cooldown = self.shoot_cooldown_max
            if self.sound_manager:
                self.sound_manager('shoot')
            return bullet_pos.x, bullet_pos.y, bullet_vel.x, bullet_vel.y
        return None

    def draw(self, screen):
        rad = math.radians(self.angle)
        
        # SLEEK FUTURISTIC SPACESHIP DESIGN
        
        # Main body - elongated hexagon
        front_tip = (
            self.pos.x + math.cos(rad) * self.radius * 2.5,
            self.pos.y - math.sin(rad) * self.radius * 2.5
        )
        
        front_left = (
            self.pos.x + math.cos(rad + 0.4) * self.radius * 1.8,
            self.pos.y - math.sin(rad + 0.4) * self.radius * 1.8
        )
        
        front_right = (
            self.pos.x + math.cos(rad - 0.4) * self.radius * 1.8,
            self.pos.y - math.sin(rad - 0.4) * self.radius * 1.8
        )
        
        mid_left = (
            self.pos.x + math.cos(rad + 1.2) * self.radius * 1.3,
            self.pos.y - math.sin(rad + 1.2) * self.radius * 1.3
        )
        
        mid_right = (
            self.pos.x + math.cos(rad - 1.2) * self.radius * 1.3,
            self.pos.y - math.sin(rad - 1.2) * self.radius * 1.3
        )
        
        back_left = (
            self.pos.x + math.cos(rad + 2.8) * self.radius * 0.7,
            self.pos.y - math.sin(rad + 2.8) * self.radius * 0.7
        )
        
        back_right = (
            self.pos.x + math.cos(rad - 2.8) * self.radius * 0.7,
            self.pos.y - math.sin(rad - 2.8) * self.radius * 0.7
        )
        
        back_center = (
            self.pos.x - math.cos(rad) * self.radius * 0.8,
            self.pos.y + math.sin(rad) * self.radius * 0.8
        )
        
        # Main body gradient (dark to bright)
        body_points = [front_tip, front_right, mid_right, back_right, back_center, back_left, mid_left, front_left]
        
        # Draw body with gradient effect
        pygame.draw.polygon(screen, (20, 80, 120), body_points)
        pygame.draw.polygon(screen, (0, 200, 255), body_points, 3)
        
        # Side panels/wings (extended)
        wing_left_outer = (
            self.pos.x + math.cos(rad + 1.8) * self.radius * 2.2,
            self.pos.y - math.sin(rad + 1.8) * self.radius * 2.2
        )
        
        wing_right_outer = (
            self.pos.x + math.cos(rad - 1.8) * self.radius * 2.2,
            self.pos.y - math.sin(rad - 1.8) * self.radius * 2.2
        )
        
        # Draw wings
        pygame.draw.polygon(screen, (10, 60, 100), [mid_left, wing_left_outer, back_left])
        pygame.draw.polygon(screen, (0, 150, 200), [mid_left, wing_left_outer, back_left], 2)
        
        pygame.draw.polygon(screen, (10, 60, 100), [mid_right, wing_right_outer, back_right])
        pygame.draw.polygon(screen, (0, 150, 200), [mid_right, wing_right_outer, back_right], 2)
        
        # Cockpit (glowing center)
        cockpit_center = (
            self.pos.x + math.cos(rad) * self.radius * 0.8,
            self.pos.y - math.sin(rad) * self.radius * 0.8
        )
        
        # Cockpit glow
        glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 255, 255, 100), (15, 15), 15)
        screen.blit(glow_surf, (cockpit_center[0] - 15, cockpit_center[1] - 15), special_flags=pygame.BLEND_ADD)
        
        pygame.draw.circle(screen, (100, 255, 255), (int(cockpit_center[0]), int(cockpit_center[1])), 5)
        pygame.draw.circle(screen, (0, 200, 255), (int(cockpit_center[0]), int(cockpit_center[1])), 5, 1)
        
        # Engine details (two smaller circles at back)
        engine_left = (
            self.pos.x + math.cos(rad + 2.5) * self.radius * 0.5,
            self.pos.y - math.sin(rad + 2.5) * self.radius * 0.5
        )
        
        engine_right = (
            self.pos.x + math.cos(rad - 2.5) * self.radius * 0.5,
            self.pos.y - math.sin(rad - 2.5) * self.radius * 0.5
        )
        
        pygame.draw.circle(screen, (50, 150, 200), (int(engine_left[0]), int(engine_left[1])), 3)
        pygame.draw.circle(screen, (50, 150, 200), (int(engine_right[0]), int(engine_right[1])), 3)

        # Thrust flame effect
        if self.thrusting:
            # Left engine flame
            flame_base_left = engine_left
            flame_length = 15 + random.randint(-3, 3)
            flame_tip_left = (
                flame_base_left[0] - math.cos(rad) * flame_length,
                flame_base_left[1] + math.sin(rad) * flame_length
            )
            
            flame_side_left1 = (
                flame_base_left[0] - math.cos(rad + 0.5) * flame_length * 0.6,
                flame_base_left[1] + math.sin(rad + 0.5) * flame_length * 0.6
            )
            
            flame_side_left2 = (
                flame_base_left[0] - math.cos(rad - 0.5) * flame_length * 0.6,
                flame_base_left[1] + math.sin(rad - 0.5) * flame_length * 0.6
            )
            
            # Right engine flame
            flame_base_right = engine_right
            flame_tip_right = (
                flame_base_right[0] - math.cos(rad) * flame_length,
                flame_base_right[1] + math.sin(rad) * flame_length
            )
            
            flame_side_right1 = (
                flame_base_right[0] - math.cos(rad + 0.5) * flame_length * 0.6,
                flame_base_right[1] + math.sin(rad + 0.5) * flame_length * 0.6
            )
            
            flame_side_right2 = (
                flame_base_right[0] - math.cos(rad - 0.5) * flame_length * 0.6,
                flame_base_right[1] + math.sin(rad - 0.5) * flame_length * 0.6
            )
            
            # Animated flame colors
            flicker = 200 + int(55 * math.sin(time.time() * 30))
            flame_color_inner = (255, flicker, 0, 255)
            flame_color_outer = (255, 100, 0, 180)
            
            flame_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            
            # Draw flames
            pygame.draw.polygon(flame_surface, flame_color_outer, 
                              [flame_base_left, flame_side_left1, flame_tip_left, flame_side_left2])
            pygame.draw.polygon(flame_surface, flame_color_inner, 
                              [flame_base_left, flame_side_left1, flame_tip_left, flame_side_left2], 1)
            
            pygame.draw.polygon(flame_surface, flame_color_outer, 
                              [flame_base_right, flame_side_right1, flame_tip_right, flame_side_right2])
            pygame.draw.polygon(flame_surface, flame_color_inner, 
                              [flame_base_right, flame_side_right1, flame_tip_right, flame_side_right2], 1)
            
            screen.blit(flame_surface, (0, 0), special_flags=pygame.BLEND_ADD)

        # Draw thrust particles
        for particle in self.thrust_particles:
            alpha = int(255 * (1 - particle['age'] / particle['max_age']))
            color = (255, 180, 50, alpha)
            size = int(4 * (1 - particle['age'] / particle['max_age']))
            if size > 0:
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (size, size), size)
                screen.blit(surf, (particle['pos'].x - size, particle['pos'].y - size), special_flags=pygame.BLEND_ADD)

    def respawn(self):
        self.pos = self.respawn_pos.copy()
        self.speed = pygame.Vector2(0, 0)
        self.angle = 0
        self.update_rect()
        self.thrust_start_time = None
        self.thrust_particles.clear()
