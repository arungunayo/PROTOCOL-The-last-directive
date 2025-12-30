import pygame
from settings import FADE_SPEED

class Fade:
    def __init__(self, size):
        self.surface = pygame.Surface(size)
        self.surface.fill((0, 0, 0))
        self.alpha = 0
        self.active = False

    def start(self):
        self.alpha = 0
        self.active = True

    def update(self):
        if not self.active:
            return False
        self.alpha += FADE_SPEED
        if self.alpha >= 255:
            self.alpha = 255
            self.active = False
            return True
        return False

    def draw(self, screen):
        if self.alpha > 0:
            self.surface.set_alpha(self.alpha)
            screen.blit(self.surface, (0, 0))
