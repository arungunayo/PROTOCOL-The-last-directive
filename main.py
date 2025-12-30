import pygame, sys
from state_manager import StateManager
from game_context import GameContext
from settings import *

from scenes.boot_scene import BootScene
from scenes.level1_scene import Level1Scene
from scenes.level2_scene import Level2Scene
from scenes.level3_scene import Level3Scene
from scenes.level4_scene import Level4Scene
from flow import Flow

pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

Flow.MAP = {
    "boot": BootScene,
    "level1": Level1Scene,
    "level2": Level2Scene,
    "level3": Level3Scene,
    "level4": Level4Scene
}

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
