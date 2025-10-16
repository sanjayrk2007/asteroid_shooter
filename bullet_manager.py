import pygame
from bullet import Bullet

class BulletManager:
    def __init__(self, font, sound_manager=None):
        self.bullets = []
        self.bullet_font = font
        self.sound_manager = sound_manager

    def add(self, bullet):
        bullet.font = self.bullet_font
        bullet.sound_manager = self.sound_manager
        self.bullets.append(bullet)
        if self.sound_manager:
            self.sound_manager('shoot')

    def update(self):
        for bullet in self.bullets[:]:
            bullet.update()
            w, h = pygame.display.get_surface().get_size()
            if bullet.lifespan <= 0 or not (0 <= bullet.pos.x <= w and 0 <= bullet.pos.y <= h):
                self.bullets.remove(bullet)

    def draw(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)
