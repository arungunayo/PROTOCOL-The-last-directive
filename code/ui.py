import pygame
from settings import *

class DialogueBox:
    def __init__(self, font_size=24):
        # Configuration
        self.font = pygame.font.SysFont("Courier New", font_size, bold=True)
        self.text_color = (0, 255, 100)  # Terminal Green
        self.bg_color = (0, 20, 0, 220)  # Darker, slightly opaque bg
        self.border_color = (0, 200, 80)
        
        # Dimensions
        self.padding = 20
        self.width = WINDOW_WIDTH - 100
        self.height = 200
        self.rect = pygame.Rect(50, 20, self.width, self.height)
        
        # State
        self.active = False
        self.target_text = ""
        self.display_text = ""
        self.char_index = 0
        self.last_update = 0
        self.typing_speed = 20  # Fast typing
        
        # Text Rendering
        self.line_height = self.font.get_height() + 5
        self.max_lines = (self.height - (self.padding * 2)) // self.line_height

    def show_message(self, message):
        """Start showing a new message."""
        self.target_text = message
        self.display_text = ""
        self.char_index = 0
        self.active = True
        self.last_update = pygame.time.get_ticks()

    def update(self):
        if not self.active:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.typing_speed:
            if self.char_index < len(self.target_text):
                self.display_text += self.target_text[self.char_index]
                self.char_index += 1
                self.last_update = current_time

    def _wrap_text(self, text):
        """
        Splits text into lines that fit within the box width.
        Respects existing newlines.
        """
        lines = []
        # split by existing newlines first
        paragraphs = text.split('\n')
        
        for paragraph in paragraphs:
            words = paragraph.split(' ')
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                fw, _ = self.font.size(test_line)
                
                if fw < (self.width - (self.padding * 2)):
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word + " "
            lines.append(current_line)
            
        return lines

    def draw(self, surface):
        if not self.active:
            return

        # 1. Draw Background & Border
        bg_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_surface.fill(self.bg_color)
        surface.blit(bg_surface, self.rect.topleft)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # 2. Wrap and Render Text
        lines = self._wrap_text(self.display_text)

        # Scroll: If too many lines, show only the last N lines
        if len(lines) > self.max_lines:
            lines = lines[-self.max_lines:]

        for i, line in enumerate(lines):
            text_surf = self.font.render(line, True, self.text_color)
            pos_x = self.rect.x + self.padding
            pos_y = self.rect.y + self.padding + (i * self.line_height)
            surface.blit(text_surf, (pos_x, pos_y))
