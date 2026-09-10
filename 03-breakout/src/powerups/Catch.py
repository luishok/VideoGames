import pygame
import settings

class Catch:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y 
        self.width = 16
        self.height = 16
        self.active = True
        self.vy = settings.POWERUP_SPEED

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, target) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y > settings.VIRTUAL_HEIGHT:
            self.active = False

    def render(self, surface: pygame.Surface) -> None: 
        surface.blit(
            settings.TEXTURES["spritesheet"],
            (round(self.x), round(self.y)),
            settings.FRAMES["powerups"][7],
        )

    def take(self, state) -> None:
        state.catch_powerup_active = True
        self.active = False
        state.catch_timer = 10.0
        