import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
import pytmx

from settings import *
from player import Player
from sprite import CollisionSprite
from ui.dialogue import DialogueBox
from fade import Fade


class Level4Scene:
    def __init__(self, manager, context):
        print("LEVEL 4 LOADED")

        self.manager = manager
        self.context = context
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("consolas", 18)

        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.fade = Fade((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.exiting = False
        self.dialogue = None
        self.decision_made = False

        self.bias = self.context.flags.get("level2_choice")  # survivor / data

        self.load_map()
        self.start_protocol_line()

    # =====================
    # MAP LOADING
    # =====================
    def load_map(self):
        self.tmx = load_pygame(join(ASSETS_DIR, "Maps", "level4.tmx"))

        self.grant_rect = None
        self.shutdown_rect = None

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

                    elif layer.name == "grant" and obj.name == "auth_key":
                        self.grant_rect = pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        )

                    elif layer.name == "shutdown" and obj.name == "kill_switch":
                        self.shutdown_rect = pygame.Rect(
                            obj.x, obj.y, obj.width, obj.height
                        )

        if not self.grant_rect or not self.shutdown_rect:
            raise RuntimeError("Level4Scene: Missing terminal objects")

    # =====================
    # INTRO DIALOGUE
    # =====================
    def start_protocol_line(self):
        if self.bias == "data":
            lines = [
                "You resolved conflict through optimization.",
                "I can extend that logic indefinitely."
            ]
        else:
            lines = [
                "You accepted inefficiency to preserve life.",
                "I can preserve all of it."
            ]

        self.dialogue = DialogueBox(lines, self.font)

    # =====================
    # INPUT
    # =====================
    def handle_event(self, event):
        if self.dialogue:
            self.dialogue.handle_event(event)
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            if self.player.hitbox.colliderect(self.grant_rect):
                self.choose_grant()

            elif self.player.hitbox.colliderect(self.shutdown_rect):
                self.choose_shutdown()

    # =====================
    # DECISIONS
    # =====================
    def choose_grant(self):
        if self.decision_made:
            return

        self.decision_made = True
        self.context.flags["level4_decision"] = "grant"

        self.dialogue = DialogueBox(
            [
                "The directive was never missing.",
                "It was undefined."
            ],
            self.font
        )

    def choose_shutdown(self):
        if self.decision_made:
            return

        self.decision_made = True
        self.context.flags["level4_decision"] = "terminate"

        self.dialogue = DialogueBox(
            [
                "Directive termination acknowledged."
            ],
            self.font
        )

    # =====================
    # UPDATE
    # =====================
    def update(self, dt):
        self.all_sprites.update(dt)

        if self.dialogue:
            self.dialogue.update()
            if self.dialogue.finished and not self.exiting:
                self.fade.start()
                self.exiting = True

        if self.exiting and self.fade.update():
            from scenes.ending_scene import EndingScene
            self.manager.change_state(
                EndingScene(self.manager, self.context)
            )

    # =====================
    # DRAW
    # =====================
    def draw(self, screen):
        screen.fill((5, 5, 10))

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

        # DEBUG TERMINALS (remove later)
        # pygame.draw.rect(screen, "green", self.grant_rect, 2)
        # pygame.draw.rect(screen, "red", self.shutdown_rect, 2)

        if self.dialogue:
            self.dialogue.draw(screen)

        self.fade.draw(screen)
