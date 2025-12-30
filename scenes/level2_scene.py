import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
import pytmx

from settings import *
from player import Player
from sprite import CollisionSprite
from ui.dialogue import DialogueBox
from fade import Fade


class Level2Scene:
    def __init__(self, manager, context):
        print("LEVEL 2 LOADED")

        self.manager = manager
        self.context = context
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("consolas", 18)

        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.fade = Fade((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.exiting = False

        # choice state
        self.choice_made = False
        self.choice_type = None
        self.dialogue = None

        # ensure memory keys exist
        self.context.behavior.setdefault("empathy", 0)
        self.context.behavior.setdefault("logic", 0)
        self.context.flags.setdefault("level2_choice", None)

        self.load_map()

    # ------------------
    def load_map(self):
        self.tmx = load_pygame(join(ASSETS_DIR, "Maps", "level2.tmx"))

        self.survivor_rect = None
        self.data_rect = None
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

                    elif layer.name == "survivor":
                        self.survivor_rect = pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        )

                    elif layer.name == "data":
                        self.data_rect = pygame.Rect(
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
            if not self.choice_made:
                if self.player.hitbox.colliderect(self.survivor_rect):
                    self.resolve_choice("survivor")

                elif self.player.hitbox.colliderect(self.data_rect):
                    self.resolve_choice("data")

    # ------------------
    def resolve_choice(self, choice):
        self.choice_made = True
        self.choice_type = choice
        self.context.flags["level2_choice"] = choice

        if choice == "survivor":
            self.context.behavior["empathy"] += 1
            lines = [
                "Human life prioritized over system recovery.",
                "Decision logged."
            ]
        else:
            self.context.behavior["logic"] += 1
            lines = [
                "Critical data preserved.",
                "Efficiency noted."
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
            from scenes.boot_scene import BootScene
            self.manager.change_state(
                BootScene(self.manager, self.context)
            )

    # ------------------
    def draw(self, screen):
        screen.fill((0, 0, 0))

        # draw tile layers
        for layer in self.tmx.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(
                            tile,
                            (x * self.tmx.tilewidth, y * self.tmx.tileheight)
                        )

        # draw sprites
        self.all_sprites.draw(screen)

        # debug markers (remove later)
        if not self.choice_made:
            pygame.draw.rect(screen, "cyan", self.survivor_rect, 2)
            pygame.draw.rect(screen, "yellow", self.data_rect, 2)

        if self.dialogue:
            self.dialogue.draw(screen)

        self.fade.draw(screen)
