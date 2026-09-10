"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class TitleScreenState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World


class TitleScreenState(BaseState):
    def enter(self) -> None:
        self.world = World()

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        title_text = settings.FONTS["flappy"].render("Flappy Bird", True, settings.COLOR_WHITE)
        title_rect = title_text.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 3)
        )
        surface.blit(title_text, title_rect)

        # Instrucciones para elegir modo
        sub_text = settings.FONTS["medium"].render("Presiona 1 para Normal", True, settings.COLOR_WHITE)
        sub_rect = sub_text.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 10)
        )
        surface.blit(sub_text, sub_rect)

        hard_text = settings.FONTS["medium"].render("Presiona 2 para Dificil", True, settings.COLOR_WHITE)
        hard_rect = hard_text.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 50)
        )
        surface.blit(hard_text, hard_rect)
    def on_input(self, input_id: str, input_data: InputData) -> None:

        if input_data.pressed:
            if input_id == "normal_mode":  # Asumiendo que configuras la tecla '1'
                self.state_machine.change("count_down", mode="normal")
            elif input_id == "hard_mode":  # Asumiendo que configuras la tecla '2'
                self.state_machine.change("count_down", mode="hard")
        # if input_id == "confirm" and input_data.pressed:
        #     self.state_machine.change("count_down")
