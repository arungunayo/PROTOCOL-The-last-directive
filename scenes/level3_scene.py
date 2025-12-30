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


class Level3Scene:
    def __init__(self, manager, context):
        print("LEVEL 3 LOADED")
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
        self.trigger_ai_response(self.context.ai.generate_mission_briefing, "Sector 6 - The Archives")

        self.branch = self.context.flags.get("level2_choice")

        if self.branch not in ("survivor", "data"):
            raise RuntimeError("Level3Scene: Invalid branch state")

        self.load_map()

    def trigger_ai_response(self, func, *args):
        """Helper to run AI calls in a separate thread."""
        def wrapper():
            response = func(*args)
            if isinstance(response, dict):
                msg = f">> ARCHIVE ACCESS <<\n\nOBJECTIVE: {response.get('surface_objective')}\n\n[MEMETIC HAZARD]: {response.get('hidden_evaluation')}"
                self.ui.show_message(msg)
            else:
                self.ui.show_message(response)
        
        threading.Thread(target=wrapper, daemon=True).start()

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

        self.ui.show_message(lines) # Changed from self.dialogue = DialogueBox(lines, self.font)
    # =========================
    # INPUT
    # =========================
    def handle_event(self, event):
        if self.ui.is_active(): # Check if UI is active instead of self.dialogue
            self.ui.handle_event(event)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.fade.start()
                self.exiting = True
                
            # AI Testing Keys
            elif event.key == pygame.K_t:
                self.trigger_ai_response(self.context.ai.analyze_action, "Player read a forbidden file.", "Information gathering.")
            
            elif event.key == pygame.K_e:
                self.trigger_ai_response(self.context.ai.generate_terminal_log, "Sector 6 Archives")
                
            elif event.key == pygame.K_q:
                self.trigger_ai_response(self.context.ai.generate_end_report)

            # Existing K_i logic
            elif event.key == pygame.K_i:
                if self.branch == "survivor":
                    if self.player.hitbox.colliderect(self.escort_rect):
                        self.finish_level("empathy")

                elif self.branch == "data":
                    if self.player.hitbox.colliderect(self.node_rect):
                        self.finish_level("logic")

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
        for layer in self.tmx.visible_layers: # Kept TMX drawing
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx.get_tile_image_by_gid(gid)
                    if tile:
                        screen.blit(
                            tile,
                            (x * self.tmx.tilewidth, y * self.tmx.tileheight)
                        )

        self.all_sprites.draw(screen)
        
        self.ui.draw(screen)
        self.fade.draw(screen)
        if self.branch == "survivor":
            pygame.draw.rect(screen, "green", self.escort_rect, 2)
        else:
            self.dialogue.draw(screen)

        self.fade.draw(screen)
