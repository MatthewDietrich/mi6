import random

import pygame
import pygame.locals

from src.config import *


class Die:
    RED = "r"
    GREEN = "g"
    BLUE = "b"
    WHITE = "w"

    def __init__(
        self, color: str, pos: tuple[int, int], player=0, in_game=True
    ) -> None:
        self.color = color
        match color:
            case self.RED:
                self.active_draw_color = (128, 0, 0, 255)
                self.inactive_draw_color = (64, 0, 0, 255)
                self.hover_active_draw_color = (255, 0, 0, 255)
                self.hover_inactive_draw_color = (92, 0, 0, 255)
                self.pip_color = (255, 255, 255, 255)
                self.color_word = "Red"
            case self.GREEN:
                self.active_draw_color = (0, 128, 0, 255)
                self.inactive_draw_color = (0, 64, 0, 255)
                self.hover_active_draw_color = (0, 255, 0, 255)
                self.hover_inactive_draw_color = (0, 92, 0, 255)
                self.pip_color = (255, 255, 255, 255)
                self.color_word = "Green"
            case self.BLUE:
                self.active_draw_color = (0, 0, 192, 255)
                self.inactive_draw_color = (0, 0, 64, 255)
                self.hover_active_draw_color = (0, 0, 255, 255)
                self.hover_inactive_draw_color = (0, 0, 92, 255)
                self.pip_color = (255, 255, 255, 255)
                self.color_word = "Blue"
            case self.WHITE:
                self.active_draw_color = (192, 192, 192, 255)
                self.inactive_draw_color = (64, 64, 64, 255)
                self.hover_active_draw_color = (255, 255, 255, 255)
                self.hover_inactive_draw_color = (92, 92, 92, 255)
                self.pip_color = (0, 0, 0, 255)
                self.color_word = "White"
            case _:
                raise ValueError("Die color must be r, g, b, or w.")
        self.value = 1
        self.pos = pos
        self.rect = pygame.Rect(pos[0], pos[1], DIE_SIZE, DIE_SIZE)
        self.surf = pygame.Surface((DIE_SIZE, DIE_SIZE), pygame.DOUBLEBUF)
        self.in_game = in_game
        self.hover = False
        self.player = player
        self.blocked = False
        self.activated = False

    def __str__(self) -> str:
        player_addendum = ""
        if self.color == Die.BLUE:
            player_addendum = f" (Player {self.player})"
        return f"{self.color_word} {self.value}{player_addendum}"

    def roll(self) -> None:
        self.value = random.randint(1, 6)
        self._draw_to_surf()

    def face(self, value: int) -> None:
        self.value = value
        self._draw_to_surf()

    def blit_to_surf(self, surf: pygame.Surface) -> None:
        surf.blit(self.surf, self.pos)

    def set_hover(self, value: bool) -> None:
        self.hover = value
        self._draw_to_surf()

    def set_blocked(self, value: bool) -> None:
        self.blocked = value
        self._draw_to_surf

    def set_activated(self, value: bool) -> None:
        self.activated = value
        self._draw_to_surf()

    def _draw_pip(self, x, y) -> None:
        pygame.draw.circle(self.surf, self.pip_color, (x, y), DIE_PIP_RADIUS)

    def _draw_to_surf(self) -> None:
        if self.activated:
            draw_color = (255, 140, 0)
        else:
            if self.hover:
                draw_color = self.hover_active_draw_color
                if self.blocked:
                    draw_color = self.hover_inactive_draw_color
            else:
                draw_color = self.active_draw_color
                if self.blocked:
                    draw_color = self.inactive_draw_color

        self.surf.fill(BACKGROUND_COLOR)
        pygame.draw.rect(
            self.surf, draw_color, (0, 0, DIE_SIZE, DIE_SIZE), 0, DIE_PIP_RADIUS
        )
        if self.value % 2 != 0:
            self._draw_pip(DIE_SIZE / 2, DIE_SIZE / 2)
        if self.value >= 2:
            self._draw_pip(2 * DIE_PIP_RADIUS, 2 * DIE_PIP_RADIUS)
            self._draw_pip(
                DIE_SIZE - 2 * DIE_PIP_RADIUS,
                DIE_SIZE - 2 * DIE_PIP_RADIUS,
            )
        if self.value >= 4:
            self._draw_pip(
                DIE_SIZE - 2 * DIE_PIP_RADIUS,
                2 * DIE_PIP_RADIUS,
            )
            self._draw_pip(
                2 * DIE_PIP_RADIUS,
                DIE_SIZE - 2 * DIE_PIP_RADIUS,
            )
        if self.value == 6:
            self._draw_pip(
                DIE_SIZE - 2 * DIE_PIP_RADIUS,
                DIE_SIZE / 2,
            )
            self._draw_pip(
                2 * DIE_PIP_RADIUS,
                DIE_SIZE / 2,
            )
