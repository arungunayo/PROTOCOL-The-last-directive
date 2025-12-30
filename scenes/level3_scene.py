import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
import pytmx

from settings import *
from player import Player
from sprite import CollisionSprite
from ui.dialogue import DialogueBox
from fade import Fade


class Level3Scene:
    def __init__(self, manager, context):
        print("LEVEL 3 LOADED")

        self.manager = manager
        self.context = context
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("consolas", 18)

        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.fade = Fade((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.exiting = False
        self.dialogue = None

        self.branch = self.context.flags.get("level2_choice")

        if self.branch not in ("survivor", "data"):
            raise RuntimeError("Level3Scene: Invalid branch state")

        self.load_map()

    # ------------------
    def load_map(self):
        self.tmx = load_pygame(join(ASSETS_DIR, "Maps", "level3.tmx"))

        self.escort_rect = None
        self.node_rect = None
        self.exit_rect = None

        for layer in self.tmx.layers:
            if isinstance(layer, pytmx.TiledObjectGroup):
                for obj in layer:
                    if layer.name == "platform":
                        CollisionSprite(
                            pygame.FRect(obj.x, obj.y, obj.width, obj.height),
                            self.collision_sprites
                        )

                    elif layer.name == "player" and obj.name == "spawn":
                        self.player = Player(
                            (obj.x, obj.y),
                            self.all_sprites,
                            self.collision_sprites
                        )

                    elif layer.name == "escort":
                        self.escort_rect = pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        )

                    elif layer.name == "node":
                        self.node_rect = pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        )

                    elif layer.name == "exit":
                        self.exit_rect = pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        )

    # ------------------
    def handle_event(self, event):
        if self.dialogue:
            self.dialogue.handle_event(event)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            if self.branch == "survivor":
                if self.player.hitbox.colliderect(self.escort_rect):
                    self.finish_level("empathy")

            elif self.branch == "data":
                if self.player.hitbox.colliderect(self.node_rect):
                    self.finish_level("logic")

    # ------------------
    def finish_level(self, path):
        if path == "empathy":
            lines = [
                "You preserve life even when it complicates the task."
            ]
        else:
            lines = [
                "You remove obstacles without hesitation."
            ]

        self.dialogue = DialogueBox(lines, self.font)

    # ------------------
    def update(self, dt):
        self.all_sprites.update(dt)

        if self.dialogue:
            self.dialogue.update()
            if self.dialogue.finished and not self.exiting:
                self.fade.start()
                self.exiting = True

        if self.exiting and self.fade.update():
            from scenes.final_scene import FinalScene
            self.manager.change_state(
                FinalScene(self.manager, self.context)
            )

    # ------------------
    def draw(self, screen):
        # BRANCH-BASED MOOD
        if self.branch == "survivor":
            screen.fill((20, 20, 30))  # warmer
        else:
            screen.fill((5, 5, 15))    # colder

        for layer in self.tmx.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(
                            tile,
                            (x * self.tmx.tilewidth, y * self.tmx.tileheight)
                        )

        self.all_sprites.draw(screen)

        # DEBUG (REMOVE LATER)
        if self.branch == "survivor":
            pygame.draw.rect(screen, "green", self.escort_rect, 2)
        else:
            pygame.draw.rect(screen, "red", self.node_rect, 2)

        if self.dialogue:
            self.dialogue.draw(screen)

        self.fade.draw(screen)
