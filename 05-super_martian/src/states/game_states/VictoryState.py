import pygame
from gale.state import BaseState
from gale.timer import Timer
import settings

class VictoryState(BaseState):
    def enter(self, **enter_params) -> None:

        self.level = enter_params.get("level", 1)
        self.game_level = enter_params.get("game_level")
        self.player = enter_params.get("player")
        self.camera = enter_params.get("camera")
        
        self.radius = int((settings.VIRTUAL_WIDTH ** 2 + settings.VIRTUAL_HEIGHT ** 2) ** 0.5)

        pygame.mixer.music.stop()
        settings.SOUNDS["victory"].play()

        Timer.tween(1.5, [(self, {"radius": 0})])

        Timer.after(1.5, self._on_transition_complete)
       

    def update(self, dt: float) -> None:
        self.camera.update(dt)

    def render(self, surface: pygame.Surface) -> None:

        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255)) # Relleno negro opaco

        center_x = settings.VIRTUAL_WIDTH // 2
        center_y = settings.VIRTUAL_HEIGHT // 2

        pygame.draw.circle(overlay, (0, 0, 0, 0), (center_x, center_y), self.radius)

        surface.blit(overlay, (0, 0))

    def _on_transition_complete(self) -> None:
        if self.level == 1:
            self.player.won = False
            print("¡Avanzando al Nivel 2!")
            self.state_machine.change(
                "play", 
                level=2, 
                player=self.player
            )
        else:
            print("¡Juego completado! Volviendo al menú...")
            self.state_machine.change("start")