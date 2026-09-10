import pygame
import settings


class PowerUp:
    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = 20
        self.height: float = 20
        self.is_out: bool = False


    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, rect: pygame.Rect) -> bool:
        return self.get_rect().colliderect(rect)

    def update(self, dt: float) -> None:
        self.x += -settings.MAIN_SCROLL_SPEED * dt

        if self.x < -self.width:
            self.is_out = True

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x + 10), int(self.y + 10)), 10)