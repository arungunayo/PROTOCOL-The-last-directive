import pygame
from os import walk
from os.path import dirname, abspath, join

BASE_DIR = dirname(abspath(__file__))
ASSETS_DIR = join(BASE_DIR, "assets")


WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 64

TEXT_SPEED = 35        # typewriter speed (ms)
FADE_SPEED = 12
