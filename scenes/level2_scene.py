import pygame
from os.path import join
from pytmx.util_pygame import load_pygame
import pytmx

from settings import *
from player import Player
from sprite import Sprite, Decoration, CollisionSprite
from fade import Fade
from ai_ui import DialogueBox
import threading


class Level2Scene:
    def __init__(self, manager, context):
        print("LEVEL 2 LOADED")

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
        
        # UI
        self.ui = DialogueBox()

        self.setup()
        
        # Trigger Briefing
        self.trigger_ai_response(self.context.ai.generate_mission_briefing, "Sector 9 - Industrial Core")

        # ensure memory keys exist
        self.context.behavior.setdefault("empathy", 0)
        self.context.behavior.setdefault("logic", 0)
        self.context.flags.setdefault("level2_choice", None)

        self.load_map()

    def trigger_ai_response(self, func, *args):
        """Helper to run AI calls in a separate thread."""
        def wrapper():
            response = func(*args)
            if isinstance(response, dict):
                msg = f">> GEN 2 BRIEFING <<\n\nOBJECTIVE: {response.get('surface_objective')}\n\n[PSY-OP]: {response.get('hidden_evaluation')}"
                self.ui.show_message(msg)
            else:
                self.ui.show_message(response)
        
        threading.Thread(target=wrapper, daemon=True).start()

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

    # =========================
    # UPDATE
    # =========================
    def update(self, dt):
        self.all_sprites.update(dt)
        self.ui.update()

        # camera follow
        self.camera_offset.x = (
            self.player.rect.centerx - WINDOW_WIDTH // 2
        )
        self.camera_offset.y = (
            self.player.rect.centery - WINDOW_HEIGHT // 2
        )

        # exit transition
        if self.exiting and self.fade.update():
            # FOR NOW, LOOP BACK TO BOOT
            # LATER: Go to Level 3 or Main Menu
            from scenes.boot_scene import BootScene
            self.manager.change_state(
                BootScene(self.manager, self.context)
            )

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        if not self.choice_made:
            pygame.draw.rect(screen, "cyan", self.survivor_rect, 2)
            pygame.draw.rect(screen, "yellow", self.data_rect, 2)

        if self.dialogue:
            self.dialogue.draw(screen)

        self.fade.draw(screen)
