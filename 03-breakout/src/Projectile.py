import pygame
import settings

class Projectile:

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.active = True
        self.vy = -2 * settings.POWERUP_SPEED

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y < 0:
            self.active = False

    def render(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 100, 50), self.get_rect())