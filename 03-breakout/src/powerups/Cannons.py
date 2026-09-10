import pygame
import settings

class Cannons:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y 
        self.width = 16
        self.height = 16
        self.active = True
        self.vy = settings.POWERUP_SPEED

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, target) -> bool:
        # Construimos el rectángulo manualmente leyendo las propiedades del target (la paleta)
        target_rect = pygame.Rect(target.x, target.y, target.width, target.height)
        return self.get_rect().colliderect(target_rect)

    def update(self, dt: float) -> None:
        self.y += self.vy * dt
        if self.y > settings.VIRTUAL_HEIGHT:
            self.active = False

    def render(self, surface: pygame.Surface) -> None: 
        surface.blit(
            settings.TEXTURES["spritesheet"],
            (round(self.x), round(self.y)),
            settings.FRAMES["powerups"][6],
        )

    def take(self, state) -> None:
        state.cannons_active = True
        self.active = False
        state.cannons_timer = 10.0