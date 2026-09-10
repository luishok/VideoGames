"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class LogPair: a top log
(rendered flipped upside down) and a bottom log, LOGS_GAP pixels
apart, that scroll left together and score once the bird passes them.
"""

import pygame

import settings


class LogPair:
    def __init__(self, x: float, y: float, gap: float = settings.LOGS_GAP, is_moving: bool=False) -> None:
        self.x: float = x
        self.y: float = y
        self.gap: float = gap
        self.is_moving: bool = is_moving
        self.scored: bool = False

        if self.is_moving:
            self.gap_vy: float = 30.0

    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), settings.LOG_WIDTH, settings.LOG_HEIGHT)

    def get_bottom_rect(self) -> pygame.Rect:
        return pygame.Rect(
            round(self.x),
            round(self.y + self.gap + settings.LOG_HEIGHT),
            settings.LOG_WIDTH,
            settings.LOG_HEIGHT,
        )

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_top_rect().colliderect(rect) or self.get_bottom_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

        if self.is_moving:
            self.y += self.gap_vy * dt

            min_gap = 65 
            ground_y = settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT
            max_gap_allowed = ground_y - self.y - settings.LOG_HEIGHT
            max_gap = min(130, max_gap_allowed)

            if self.gap <= min_gap: 
                self.gap = min_gap
                self.gap_vy *= -1
            elif self.gap >= max_gap: 
                self.gap = max_gap
                self.gap_vy *= -1

    def is_out_of_game(self) -> bool:
        return self.x < -settings.LOG_WIDTH

    def update_scored(self, rect: pygame.Rect) -> bool:
        if self.scored:
            return False

        if rect.left > self.x + settings.LOG_WIDTH:
            self.scored = True
            return True

        return False

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["log_inverted"], self.get_top_rect())
        surface.blit(settings.TEXTURES["log"], self.get_bottom_rect())
