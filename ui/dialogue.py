import pygame
from settings import TEXT_SPEED

class DialogueBox:
    def __init__(self, lines, font):
        self.lines = lines
        self.font = font
        self.index = 0
        self.visible = True

        self.text = ""
        self.char_index = 0
        self.last_time = pygame.time.get_ticks()
        self.finished_line = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.finished_line:
                self.text = self.lines[self.index]
                self.finished_line = True
            else:
                self.index += 1
                if self.index >= len(self.lines):
                    self.visible = False
                else:
                    self.text = ""
                    self.char_index = 0
                    self.finished_line = False

    def update(self):
        if not self.visible or self.finished_line:
            return

        now = pygame.time.get_ticks()
        if now - self.last_time > TEXT_SPEED:
            self.last_time = now
            line = self.lines[self.index]
            if self.char_index < len(line):
                self.text += line[self.char_index]
                self.char_index += 1
            else:
                self.finished_line = True

    def draw(self, screen):
        box = pygame.Rect(60, 520, 1160, 140)
        pygame.draw.rect(screen, (10, 10, 10), box)
        pygame.draw.rect(screen, (80, 255, 120), box, 2)

        rendered = self.font.render(self.text, True, (200, 255, 200))
        screen.blit(rendered, (box.x + 20, box.y + 20))
