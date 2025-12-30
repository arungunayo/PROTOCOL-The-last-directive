import pygame, sys
from state_manager import StateManager
from scenes.boot_scene import BootScene
from game_context import GameContext
from settings import *

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

context = GameContext()
boot = BootScene(None, context)
manager = StateManager(boot)
boot.manager = manager

while True:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        manager.handle_event(event)

    manager.update(dt)
    manager.draw(screen)
    pygame.display.flip()
