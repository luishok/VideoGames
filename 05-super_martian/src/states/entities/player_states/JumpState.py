"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class JumpState for player.
"""

import settings
import pygame
import src.Player as Player
from src.states.entities.BaseEntityState import BaseEntityState


class JumpState(BaseEntityState):
    def enter(self) -> None:
        self.entity.change_animation("jump")
        self.entity.vy = -settings.JUMP_TAKEOFF_SPEED
        settings.SOUNDS["jump"].play()

    def update(self, dt: float) -> None:
        self.entity.jump_requested = False

        # Releasing "jump" while still ascending clamps the upward speed
        # down to JUMP_CUT_VELOCITY instead of zeroing it outright, so a
        # tap still gives a small hop rather than an abrupt stop.
        if not self.entity.jump_held and self.entity.vy < -settings.JUMP_CUT_VELOCITY:
            self.entity.vy = -settings.JUMP_CUT_VELOCITY

        if self.entity.move_direction != 0:
            self.entity.flipped = self.entity.move_direction < 0
        self.entity.vx = settings.PLAYER_SPEED * self.entity.move_direction

        if self.entity.vy >= 0:
            self.entity.change_state("fall")

        player_rect = pygame.Rect(self.entity.x, self.entity.y, self.entity.width, self.entity.height)
          
        for block in self.entity.game_level.blocks:

            if player_rect.colliderect(block.rect) and self.entity.vy < 0:
                
                if block.rect.bottom - 12 <= player_rect.top <= block.rect.bottom:
                    self.entity.y = block.rect.bottom  
                    self.entity.vy = 0                 
                    
                    block.on_hit_from_bottom(self.entity.score, target_score=200)
                    break

        