"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState for the game.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState, StateMachine

import settings
from src.definitions.entity import ENTITY_DEFS
from src.Player import Player
from src.states.entity import player as player_states
from src.world.Dungeon import Dungeon


class PlayState(BaseState):
    def enter(self) -> None:
        definition = ENTITY_DEFS["player"]

        self.player = Player(
            x=settings.VIRTUAL_WIDTH / 2 - 8,
            y=settings.VIRTUAL_HEIGHT / 2 - 11,
            width=16,
            height=22,
            walk_speed=definition["walk_speed"],
            # One heart == 2 health.
            health=6,
            animation_defs=definition["animations"],
            states={},
        )
        # Rendering/collision offset for the spaced sprite.
        self.player.offset_y = 5

        self.dungeon = Dungeon(self.player, on_game_over=self._on_game_over)

        self.player.state_machine.states = {
            "walk": lambda sm: player_states.PlayerWalkState(self.player, sm, self.dungeon),
            "idle": lambda sm: player_states.PlayerIdleState(self.player, sm, self.dungeon),
            "swing-sword": lambda sm: player_states.PlayerSwingSwordState(
                self.player, sm, self.dungeon
            ),
            "pot-lift": lambda sm: player_states.PlayerPotLiftState(
                self.player, sm, self.dungeon
            ),
            "pot-idle": lambda sm: player_states.PlayerPotIdleState(
                self.player, sm, self.dungeon
            ),
            "pot-walk": lambda sm: player_states.PlayerPotWalkState(
                self.player, sm, self.dungeon
            ),
        }
        self.player.change_state("idle")

        pygame.mixer.music.load(settings.MUSIC["dungeon"])
        pygame.mixer.music.play(loops=-1)

    def exit(self) -> None:
        pygame.mixer.music.stop()

    def _on_game_over(self) -> None:
        self.state_machine.change("game-over", player=self.player)

    def update(self, dt: float) -> None:
        self.dungeon.update(dt)
        current_room = self.dungeon.current_room
        if getattr(current_room, "is_boss_room", False):
            if getattr(current_room, "boss_defeated", False):

                self.state_machine.change("victory")

    def render(self, surface: pygame.Surface) -> None:
        self.dungeon.render(surface)

        # Draw player hearts, top of screen.
        health_left = self.player.health
        heart_frame = 1

        for i in range(3):
            if health_left > 1:
                heart_frame = 5
            elif health_left == 1:
                heart_frame = 3
            else:
                heart_frame = 1

            surface.blit(
                settings.TEXTURES["hearts"],
                (i * (settings.TILE_SIZE + 1), 2),
                settings.frame("hearts", heart_frame),
            )

            health_left -= 2

        if getattr(self.dungeon.current_room, "is_boss_room", False):
        
            boss = next((e for e in self.dungeon.current_room.entities if getattr(e, "is_boss", False) and not e.dead), None)
            
            if boss:
                boss_health_left = boss.health
  
                total_hearts_width = 3 * (settings.TILE_SIZE + 1)
                start_x = settings.VIRTUAL_WIDTH - total_hearts_width
                

                is_immune = getattr(boss, "invulnerable_to_sword", True)

                for i in range(3):
                    if boss_health_left > 1:
                        heart_frame = 5
                    elif boss_health_left == 1:
                        heart_frame = 3
                    else:
                        heart_frame = 1

                    surface.blit(
                        settings.TEXTURES["hearts"],
                        (start_x + (i * (settings.TILE_SIZE + 1)), 2),
                        settings.frame("hearts", heart_frame),
                    )

                    boss_health_left -= 2

               
                if is_immune and "shield" in settings.TEXTURES:
                    shield_x = start_x - 20 
                    shield_y = 2
                    surface.blit(settings.TEXTURES["shield"], (shield_x, shield_y))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        
        if input_id == "fire" and input_data.pressed:
            if getattr(self.player, "has_bow", False):
            
                self.player.bow.fire(self.dungeon.current_room)
                return
        self.player.on_input(input_id, input_data)