"""
Study Case: The Legend of the Princess (ARPG)
Bow class implementing the Factory Pattern for Projectiles.
"""

from typing import TypeVar
from src.Projectile import Projectile
from src.GameObject import GameObject
import settings

class Bow:
    def __init__(self, owner: TypeVar("Entity")) -> None:
        self.owner = owner 

    def fire(self, room: TypeVar("Room")) -> None:
        """
        Patrón Factory: Instancia y configura una nueva flecha (Projectile) 
        tomando como referencia la posición y dirección actual del jugador.
        """
        player = self.owner

        x = player.x + player.width // 2 - 4
        y = player.y + player.height // 2 - 4
        
        direction = player.direction

        arrow_obj = GameObject(
            {
                "type": "arrow",
                "texture": "arrow",
                "states": {"default": {"frame": 0}},
                "width": 8,
                "height": 8,
                "solid": False,
                "default_state": "default",
            },
            x,
            y
        )

        arrow = Projectile(obj=arrow_obj, direction=direction)

        room.projectiles.append(arrow)
        
        print(f"[LOG] ¡Flecha disparada hacia la dirección: {direction}!")

    def _get_dx(self, direction: str) -> float:
        if direction == "left":
            return -150.0
        elif direction == "right":
            return 150.0
        return 0.0

    def _get_dy(self, direction: str) -> float:
        if direction == "up":
            return -150.0
        elif direction == "down":
            return 150.0
        return 0.0