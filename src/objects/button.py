import pygame
import pygame.locals

from src.config import *


class Button:
    def __init__(self, pos: tuple[int, int], text: str, font: pygame.font.Font) -> None:
        self.text = text
        self.font = font
        self.surf = pygame.Surface(BUTTON_SIZE, pygame.DOUBLEBUF)
        self.text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
        self.pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], BUTTON_WIDTH, BUTTON_HEIGHT)
        self.hover = False
        self.set_text(text)

    def __str__(self) -> str:
        return self.text

    def blit_to_surf(self, surf: pygame.Surface) -> None:
        surf.blit(self.surf, self.pos)

    def _draw_to_surf(self) -> None:
        if self.hover:
            draw_color = BUTTON_HOVER_COLOR
        else:
            draw_color = BUTTON_COLOR
        self.surf.fill(BACKGROUND_COLOR)
        pygame.draw.rect(
            self.surf,
            draw_color,
            (0, 0, BUTTON_WIDTH, BUTTON_HEIGHT),
            0,
            DIE_PIP_RADIUS,
        )
        self.surf.blit(
            self.text_surf,
            self.text_surf.get_rect(center=(BUTTON_WIDTH / 2, BUTTON_HEIGHT / 2)),
        )

    def set_hover(self, value: bool) -> None:
        self.hover = value
        self._draw_to_surf()

    def set_text(self, text: str) -> None:
        self.text = text
        self.text_surf = self.font.render(text, True, BUTTON_TEXT_COLOR)
        self._draw_to_surf()
