import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
# from src.World import World


class PauseState(BaseState):
    def enter(self, bird, world, score) -> None:
        # self.world = World()
        self.world = world
        self.bird = bird
        self.world = world
        self.score = score
        
    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)

        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black overlay
        surface.blit(overlay, (0, 0))

        text = settings.FONTS["flappy"].render("PAUSA", True, settings.COLOR_WHITE)
        rect = text.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 20)
        )
        surface.blit(text, rect)


        sub_font = settings.FONTS.get("font", settings.FONTS["medium"])
        sub_text = sub_font.render("Presiona 'P' para continuar", True, settings.COLOR_WHITE)
        sub_rect = sub_text.get_rect(
            center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 20)
        )
        surface.blit(sub_text, sub_rect)

    def on_input(self, input_id: str, input_data: InputData) -> None:

        if input_id == "pause" and input_data.pressed:
            # self.state_machine.change("count_down")
            self.state_machine.change(
                "playing", bird=self.bird, world=self.world, score=self.score
            )
