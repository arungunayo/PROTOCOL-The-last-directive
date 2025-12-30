import random
import threading
import os
import sys

# Ensure we are running from the 'code' directory so relative paths work
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir:
        os.chdir(current_dir)

from settings import *
from player import Player
from pytmx.util_pygame import load_pygame
from sprite import *
from ai_manager import ProtocolAI
from ui import DialogueBox

class Game:
    def __init__(self):
        # setup
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.camera_offset = pygame.Vector2(0, 0)
        
        # AI & UI
        self.ai = ProtocolAI()
        self.ui = DialogueBox()
        
        # groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.setup()
        
        #     bg
        self.bg = pygame.image.load(join("..","assets","Graphics","bg","bg.png")).convert()
        self.bg = pygame.transform.scale(
            self.bg, (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        
        # Trigger Initial AI Briefing (Threaded to not block UI)
        self.trigger_ai_response(self.ai.get_initial_briefing)

    def trigger_ai_response(self, func, *args):
        """Helper to run AI calls in a separate thread so game doesn't freeze."""
        def wrapper():
            response = func(*args)
            
            # Handle Structured Mission Briefing (Dict)
            if isinstance(response, dict):
                msg = f">> MISSION BRIEFING <<\n\nOBJECTIVE: {response.get('surface_objective')}\n\n[HIDDEN PARAMETER]: {response.get('hidden_evaluation')}"
                self.ui.show_message(msg)
            else:
                self.ui.show_message(response)
        
        threading.Thread(target=wrapper, daemon=True).start()

    def setup(self):
        tmx_map = load_pygame(join("..", "assets", "maps", "level1-final.tmx"))

        # =========================
        # VISUAL DECORATIONS
        # =========================
        # Convert decorations to Sprites so we can check collisions if we want
        # For now, we just add them to all_sprites for drawing
        for obj in tmx_map.get_layer_by_name("decorations"):
            Decoration.from_tmx(obj, self.all_sprites)

        # =========================
        # VISUAL GROUND TILES
        # =========================
        for x, y, image in tmx_map.get_layer_by_name("Ground").tiles():
            Sprite(
                (x * TILE_SIZE, y * TILE_SIZE),
                image,
                self.all_sprites
            )

        # =========================
        # PLATFORM COLLISIONS (POLYGONS)
        # =========================
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

        # =========================
        # PLAYER SPAWN
        # =========================
        self.player = None
        for obj in tmx_map.get_layer_by_name("player"):
            if obj.name == "spawn":
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collision_sprites
                )

        if self.player is None:
            raise RuntimeError("No player spawn found in TMX map")

    def run(self):
        # Initial Mission Briefing
        self.trigger_ai_response(self.ai.generate_mission_briefing, "Sector 4 - Identifying Anomalies")

        while self.running:
            # dt
            dt = self.clock.tick()/1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    # T: Test Action
                    if event.key == pygame.K_t:
                        self.trigger_ai_response(self.ai.analyze_action, "Player inspected a broken drone.", "Curiosity expressed.")
                    
                    # E: Interact (Terminal)
                    elif event.key == pygame.K_e:
                        # Simple proximity check: interact with "environment"
                        self.trigger_ai_response(self.ai.generate_terminal_log, "Server Room")
                    
                    # Q: Quit/End Report
                    elif event.key == pygame.K_q:
                        self.trigger_ai_response(self.ai.generate_end_report)

            # update
            self.all_sprites.update(dt)
            self.ui.update()

            self.camera_offset.x = self.player.rect.centerx - WINDOW_WIDTH // 2
            self.camera_offset.y = self.player.rect.centery - WINDOW_HEIGHT // 2

            # draw
            # # draw background with parallax
            # bg_x = -self.camera_offset.x * 0.2
            # bg_y = -self.camera_offset.y * 0.2
            # self.display_surface.blit(self.bg, (bg_x, bg_y))
            self.display_surface.blit(self.bg, (0, 0))

            for sprite in self.all_sprites:
                offset_rect = sprite.rect.copy()
                offset_rect.topleft -= self.camera_offset
                self.display_surface.blit(sprite.image, offset_rect)
            for sprite in self.collision_sprites:
                debug_rect = sprite.rect.copy()
                debug_rect.topleft -= self.camera_offset
                pygame.draw.rect(self.display_surface, "red", debug_rect, 2)
            
            # Draw UI on top
            self.ui.draw(self.display_surface)

            pygame.display.update()
        # end
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()