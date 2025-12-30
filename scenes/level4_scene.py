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


class Level4Scene:
    def __init__(self, manager, context):
        print("LEVEL 4 LOADED")

        self.manager = manager
        self.context = context
        self.display_surface = pygame.display.get_surface()
        self.camera_offset = pygame.Vector2(0, 0)
        self.font = pygame.font.SysFont("consolas", 18)

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
        self.decision_made = False

        # UI
        self.ui = DialogueBox()

        self.setup()
        
        # Trigger Briefing
        self.trigger_ai_response(self.context.ai.generate_mission_briefing, "The Core - Final Judgment")

    def trigger_ai_response(self, func, *args):
        """Helper to run AI calls in a separate thread."""
        def wrapper():
            response = func(*args)
            if isinstance(response, dict):
                msg = f">> FINAL JUDGMENT <<\n\nOBJECTIVE: {response.get('surface_objective')}\n\n[PROTOCOL STATUS]: {response.get('hidden_evaluation')}"
                self.ui.show_message(msg)
            else:
                self.ui.show_message(response)
        
        threading.Thread(target=wrapper, daemon=True).start()

    def setup(self):
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

    # =========================
    # INPUT
    # =========================
    def handle_event(self, event):
        if self.dialogue:
            self.dialogue.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.fade.start()
                self.exiting = True
                
            # AI Testing Keys
            elif event.key == pygame.K_t:
                self.trigger_ai_response(self.context.ai.analyze_action, "Player reached the Core.", "Final determination pending.")
            
            elif event.key == pygame.K_e:
                self.trigger_ai_response(self.context.ai.generate_terminal_log, "The Core")
                
            elif event.key == pygame.K_q:
                self.trigger_ai_response(self.context.ai.generate_end_report)
            
            elif event.key == pygame.K_i:
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
            from scenes.boot_scene import BootScene
            self.manager.change_state(
                BootScene(self.manager, self.context)
            )

    # =========================
    # DRAW
    # =========================
    def draw(self, screen):
        # background
        screen.blit(self.bg, (0, 0))

        # world
        for sprite in self.all_sprites:
            offset_rect = sprite.rect.copy()
            offset_rect.topleft -= self.camera_offset
            screen.blit(sprite.image, offset_rect)
            
        self.ui.draw(screen)
        self.fade.draw(screen)

        # DEBUG TERMINALS (remove later)
        # pygame.draw.rect(screen, "green", self.grant_rect, 2)
        # pygame.draw.rect(screen, "red", self.shutdown_rect, 2)

        if self.dialogue:
            self.dialogue.draw(screen)

        self.fade.draw(screen)
