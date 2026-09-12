import pygame
from typing import Any
from gale.timer import Timer

class KeyBlock:
    def __init__(self, x: float, y: float, width: float, height: float, level: Any) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.level = level
        self.is_hit = False
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, dt: float) -> None:
        pass 

    def render(self, surface: pygame.Surface, camera: Any) -> None:
        
        pass
    
    def on_hit_from_bottom(self, current_score: int, target_score: int) -> None:
        if not self.is_hit and current_score >= target_score:
            self.is_hit = True
            self._spawn_key()

    def _spawn_key(self) -> None:
        print("¡Creando la llave!") 
        
        self.level.add_item({
            "item_name": "keys",
            "frame_index": 54,
            "x": self.x,
            "y": self.y,
            "width": 16,
            "height": 16,
        })

        new_key = self.level.items[-1]
        Timer.tween(0.4, [(new_key, {"y": self.y - 16})])