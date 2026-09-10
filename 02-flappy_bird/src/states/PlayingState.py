"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

from typing import Optional

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World
from src.GameModes import NormalMode, HardMode


class PlayingState(BaseState):
    def enter(self, bird= None, world: Optional[World] = None, score = 0, mode="normal") -> None:
        self.mode_name = mode

        if mode == "hard":
            self.game_mode = HardMode()
        else:
            self.game_mode = NormalMode()

        if bird is None:
            self.world = world if world is not None else World()
            self.world.reset(True)
            self.bird = Bird(
                settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
                settings.BIRD_WIDTH,
                settings.BIRD_HEIGHT,
            )
            self.score = 0
        else:
            self.bird = bird
            self.world = world
            self.score = score

        self.world.game_mode = self.game_mode
        self.ghost_timer = 0.0


    def update(self, dt: float) -> None:

        self.game_mode.update_bird_position(self.bird, dt)
        self.world.update(dt)

        if self.bird.is_ghost:
            self.ghost_timer -= dt
            if self.ghost_timer <= 0:
                self.bird.is_ghost = False
                
                # Se acabó el poder: recargamos la música de fondo de Mario
                pygame.mixer.music.load("assets/sounds/marios_way.ogg")
                pygame.mixer.music.play(-1)  # Vuelve a sonar en bucle

        # 2. Recolección del Power-Up
        for p in self.world.powerups:
            if not p.is_out and p.collides(self.bird.get_rect()):
                p.is_out = True # Lo eliminamos al recogerlo
                self.bird.is_ghost = True
                self.ghost_timer = 6.0 # 6 segundos de inmunidad
                
                # Activamos el poder: cargamos tu canción custom
                pygame.mixer.music.load("assets/sounds/boost.mp3")
                pygame.mixer.music.play(-1)

        if not self.bird.is_ghost:
            if self.world.collides(self.bird.get_rect()):
                        settings.SOUNDS["explosion"].play()
                        settings.SOUNDS["hurt"].play()
                        self.state_machine.change("count_down", mode=self.mode_name)
                        return
            # if self.world.collides(self.bird.get_rect()):
            #     settings.SOUNDS["hurt"].play()
            #     # self.state_machine.change("score", score=self.score)
            #     return


        

        if self.world.update_scored(self.bird.get_rect()):
            self.score += 1
            settings.SOUNDS["score"].play()

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            self.state_machine.change(
                "pause", bird=self.bird, world=self.world, score=self.score
            )
            return
        # if input_id == "jump" and input_data.pressed:
        #     self.bird.jump()
        self.game_mode.handle_bird_input(self.bird, input_id, input_data)