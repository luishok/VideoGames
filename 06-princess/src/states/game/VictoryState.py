"""
This file contains the class VictoryState.
"""

import pygame
from gale.state import BaseState

import settings


class VictoryState(BaseState):
    def enter(self) -> None:
        settings.SOUNDS["victory"].play() if "victory" in settings.SOUNDS else settings.SOUNDS["door"].play()

    def exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        press = pygame.key.get_pressed()
        if press[pygame.K_RETURN] or press[pygame.K_KP_ENTER]:
            
            self.state_machine.change("start")

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((15, 15, 30))

        title_font = getattr(settings, "FONTS", {}).get("large", pygame.font.Font(None, 40))
        subtitle_font = getattr(settings, "FONTS", {}).get("small", pygame.font.Font(None, 24))

        title_surf = title_font.render("¡VICTORIA!", True, (255, 215, 0)) # Color dorado
        title_rect = title_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 - 30))
        surface.blit(title_surf, title_rect)


        sub_surf = subtitle_font.render("Presiona ENTER para volver al Menú Principal", True, (255, 255, 255))
        sub_rect = sub_surf.get_rect(center=(settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2 + 20))
        surface.blit(sub_surf, sub_rect)