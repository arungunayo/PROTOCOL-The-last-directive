import pygame
from os.path import join
from pytmx.util_pygame import load_pygame

from settings import *
from player import Player
from sprite import Sprite, Decoration, CollisionSprite
from fade import Fade
# from scenes.boot_scene import BootScene


class Level1Scene:
    def __init__(self, manager, context):
        print("LEVEL 1 LOADED")
        self.manager = manager
        self.context = context

        self.display_surface = pygame.display.get_surface()
        self.camera_offset = pygame.Vector2(0, 0)

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # background
        self.bg = pygame.image.load(
            join(ASSETS_DIR, "Graphics", "bg", "bg.png")
        ).convert()
        self.bg = pygame.transform.scale(
            self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        # state
        self.fade = Fade((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.exiting = False

        self.setup()

    # =========================
    # MAP SETUP (UNCHANGED LOGIC)
    # =========================
    def setup(self):
        tmx_map = load_pygame(
            join(ASSETS_DIR, "Maps", "level1-final.tmx")
        )

        # Decorations
        for obj in tmx_map.get_layer_by_name("decorations"):
            Decoration.from_tmx(obj, self.all_sprites)

        # Ground tiles
        for x, y, image in tmx_map.get_layer_by_name("Ground").tiles():
            Sprite(
                (x * TILE_SIZE, y * TILE_SIZE),
                image,
                self.all_sprites
            )

        # Platforms (collision)
        for obj in tmx_map.get_layer_by_name("platforms"):
            points = obj.as_points
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            rect = pygame.FRect(
                min(xs),
                min(ys),
                max(xs) - min(xs),
                max(ys) - min(ys)
            )
            CollisionSprite(rect, self.collision_sprites)

        # Player spawn
        self.player = None
        for obj in tmx_map.get_layer_by_name("player"):
            if obj.name == "spawn":
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites
                )

        if self.player is None:
            raise RuntimeError("No player spawn found in level1 TMX")

    # =========================
    # INPUT
    # =========================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # TEMP EXIT CONDITION (replace with cache objective later)
            if event.key == pygame.K_RETURN:
                self.fade.start()
                self.exiting = True

    # =========================
    # UPDATE
    # =========================
    def update(self, dt):
        self.all_sprites.update(dt)

        # camera follow
        self.camera_offset.x = (
            self.player.rect.centerx - WINDOW_WIDTH // 2
        )
        self.camera_offset.y = (
            self.player.rect.centery - WINDOW_HEIGHT // 2
        )

        # exit transition
        from scenes.boot_scene import BootScene
        if self.exiting and self.fade.update():
            from scenes.boot_scene import BootScene
            self.manager.change_state(
                BootScene(self.manager, self.context)
            )

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        # background (no parallax for now)
        screen.blit(self.bg, (0, 0))

        # world
        for sprite in self.all_sprites:
            offset_rect = sprite.rect.copy()
            offset_rect.topleft -= self.camera_offset
            screen.blit(sprite.image, offset_rect)

        # DEBUG COLLISIONS (optional)
        # for sprite in self.collision_sprites:
        #     rect = sprite.rect.copy()
        #     rect.topleft -= self.camera_offset
        #     pygame.draw.rect(screen, "red", rect, 2)

        self.fade.draw(screen)
