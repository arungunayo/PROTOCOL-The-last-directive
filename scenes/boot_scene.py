import pygame
from pytmx.util_pygame import load_pygame
import pytmx
from settings import *
from player import Player
from sprite import CollisionSprite
from ui.dialogue import DialogueBox
from fade import Fade
# from scenes.level1_scene import Level1Scene


class BootScene:
    def __init__(self, manager, context):
        self.manager = manager
        self.context = context

        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.SysFont("consolas", 20)

        self.terminal_image = pygame.image.load(
            join(ASSETS_DIR, "Images", "terminal", "terminal.png")
        ).convert_alpha()

        self.terminal_rect = None
        self.terminal_draw_rect = None

        # groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        # state
        self.dialogue = None
        self.fade = Fade((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.exiting = False

        # protocol tracking
        self.context.metrics["boot_start_time"] = pygame.time.get_ticks()
        self.moved = False
        self.interacted = False

        self.load_map()

    # =========================
    # TMX LOADING (ONLY OBJECT LAYERS)
    # =========================
    def load_map(self):

        self.tmx = load_pygame(
            join(ASSETS_DIR, "Maps", "boot.tmx")
        )

        # ---------- PLATFORM COLLISIONS ----------
        for obj in self.tmx.get_layer_by_name("platform"):
            rect = pygame.FRect(obj.x, obj.y, obj.width, obj.height)
            CollisionSprite(rect, self.collision_sprites)

        # ---------- PLAYER SPAWN ----------
        self.player = None
        for obj in self.tmx.get_layer_by_name("player"):
            if obj.name == "spawn":
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites
                )

        if self.player is None:
            raise RuntimeError("BootScene: No player spawn found")

        # ---------- TERMINAL ----------
        self.terminal_rect = None
        for obj in self.tmx.get_layer_by_name("terminal"):
            if obj.name == "term-loc":
                self.terminal_rect = pygame.Rect(
                    obj.x, obj.y, obj.width, obj.height
                )

                # visual rect (sprite aligned to bottom of interaction zone)
                self.terminal_draw_rect = self.terminal_image.get_rect(
                    midbottom=self.terminal_rect.midbottom
                )

        if self.terminal_rect is None:
            raise RuntimeError("BootScene: No terminal location found")

    # =========================
    # INPUT
    # =========================
    def handle_event(self, event):
        # dialogue eats input
        if self.dialogue:
            self.dialogue.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            # record first movement (any key)
            if not self.moved:
                self.context.metrics["time_to_first_move"] = (
                    pygame.time.get_ticks()
                    - self.context.metrics["boot_start_time"]
                )
                self.moved = True
            if event.key == pygame.K_i:
                print("Pressed I")
                print("Player hitbox:", self.player.hitbox)
                print("Terminal rect:", self.terminal_rect)

            # terminal interaction
            if event.key == pygame.K_i:
                if self.player.rect.colliderect(self.terminal_rect):
                    self.start_terminal()

    # =========================
    # TERMINAL SEQUENCE
    # =========================
    def start_terminal(self):
        if self.interacted:
            return

        self.interacted = True
        self.player.flash()

        t = pygame.time.get_ticks() - self.context.metrics["boot_start_time"]
        self.context.metrics["time_to_first_interact"] = t

        if t < 4000:
            self.context.behavior["fast_learner"] = True

        if self.context.behavior["fast_learner"]:
            lines = [
                "Input detected.",
                "You adapt quickly.",
                "Observation continues."
            ]
        else:
            lines = [
                "Input detected.",
                "Adaptation achieved.",
                "Observation continues."
            ]

        self.dialogue = DialogueBox(lines, self.font)

    # =========================
    # UPDATE
    # =========================
    def update(self, dt):
        self.all_sprites.update(dt)

        if self.dialogue:
            self.dialogue.update()
            if not self.dialogue.visible and not self.exiting:
                self.fade.start()
                self.exiting = True

        if self.exiting and self.fade.update():
            from scenes.level1_scene import Level1Scene
            self.manager.change_state(
                Level1Scene(self.manager, self.context)
            )

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        screen.fill((10, 10, 15))
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
        # terminal sprite
        if self.terminal_draw_rect:
            screen.blit(self.terminal_image, self.terminal_draw_rect)

        # sprites
        self.all_sprites.draw(screen)

        # optional terminal debug
        # pygame.draw.rect(screen, "green", self.terminal_rect, 2)



        if self.dialogue:
            self.dialogue.draw(screen)

        self.fade.draw(screen)

