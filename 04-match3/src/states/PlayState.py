"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        self.is_dragging = False
        self.dragged_tile = None
        self.start_i = -1
        self.start_j = -1

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

        if self.is_dragging and self.dragged_tile:
            if pygame.mouse.get_pressed()[0]:
                pos_x, pos_y = pygame.mouse.get_pos()
                vx = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
                vy = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
                
                # Posición original RELATIVA al tablero
                orig_x = self.start_j * settings.TILE_SIZE
                orig_y = self.start_i * settings.TILE_SIZE
                
                
                mouse_x = vx - self.board.x - settings.TILE_SIZE // 2
                mouse_y = vy - self.board.y - settings.TILE_SIZE // 2

                dx = mouse_x - orig_x
                dy = mouse_y - orig_y

                # Restricción Mover solo en cruz y máximo 1 casilla
                if abs(dx) > abs(dy):
                    dy = 0
                    dx = max(-settings.TILE_SIZE, min(settings.TILE_SIZE, dx))
                else:
                    dx = 0
                    dy = max(-settings.TILE_SIZE, min(settings.TILE_SIZE, dy))

                self.dragged_tile.x = orig_x + dx
                self.dragged_tile.y = orig_y + dy
            else:
                self.is_dragging = False
                self._handle_drop()

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.is_dragging and self.dragged_tile:
            
            x_orig = self.start_j * settings.TILE_SIZE + self.board.x
            y_orig = self.start_i * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x_orig, y_orig))
            
            self.dragged_tile.render(surface, self.board.x, self.board.y)

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(surface, f"Level: {self.level}", settings.FONTS["medium"], 30, 24, (99, 155, 255), shadowed=True)
        render_text(surface, f"Score: {self.score}", settings.FONTS["medium"], 30, 52, (99, 155, 255), shadowed=True)
        render_text(surface, f"Goal: {self.goal_score}", settings.FONTS["medium"], 30, 80, (99, 155, 255), shadowed=True)
        render_text(surface, f"Timer: {self.timer}", settings.FONTS["medium"], 30, 108, (99, 155, 255), shadowed=True)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "click" and input_data.pressed:
            pos_x, pos_y = input_data.position
            vx = pos_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            vy = pos_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            
            grid_i = int((vy - self.board.y) // settings.TILE_SIZE)
            grid_j = int((vx - self.board.x) // settings.TILE_SIZE)

            if 0 <= grid_i < settings.BOARD_HEIGHT and 0 <= grid_j < settings.BOARD_WIDTH:
                self.is_dragging = True
                self.start_i = grid_i
                self.start_j = grid_j
                self.dragged_tile = self.board.tiles[grid_i][grid_j]

    def _handle_drop(self) -> None:
        # Coordenadas de retorno relativas
        orig_x = self.start_j * settings.TILE_SIZE
        orig_y = self.start_i * settings.TILE_SIZE

        dx = self.dragged_tile.x - orig_x
        dy = self.dragged_tile.y - orig_y

        grid_i = self.start_i
        grid_j = self.start_j

        threshold = settings.TILE_SIZE // 2
        if dx > threshold:
            grid_j += 1
        elif dx < -threshold:
            grid_j -= 1
        elif dy > threshold:
            grid_i += 1
        elif dy < -threshold:
            grid_i -= 1

        tile1 = self.dragged_tile
        self.dragged_tile = None

        is_in_bounds = 0 <= grid_i < settings.BOARD_HEIGHT and 0 <= grid_j < settings.BOARD_WIDTH
        is_adjacent = (grid_i != self.start_i or grid_j != self.start_j)

        if is_in_bounds and is_adjacent:
            self.active = False
            tile2 = self.board.tiles[grid_i][grid_j]

            target_orig_x = tile2.x
            target_orig_y = tile2.y

            def arrive():
                self.board.tiles[self.start_i][self.start_j] = tile2
                self.board.tiles[grid_i][grid_j] = tile1
                tile1.i, tile1.j = grid_i, grid_j
                tile2.i, tile2.j = self.start_i, self.start_j

                matches = self.board.calculate_matches_for([tile1, tile2])

                if not matches:
                    self.board.tiles[self.start_i][self.start_j] = tile1
                    self.board.tiles[grid_i][grid_j] = tile2
                    tile1.i, tile1.j = self.start_i, self.start_j
                    tile2.i, tile2.j = grid_i, grid_j
                    
                    settings.SOUNDS["error"].play()

                    Timer.tween(
                        0.25,
                        [
                            (tile1, {"x": orig_x, "y": orig_y}),
                            (tile2, {"x": target_orig_x, "y": target_orig_y})
                        ],
                        on_finish=lambda: setattr(self, 'active', True)
                    )
                else:

                    matches = self.board.calculate_matches_for([tile1, tile2])

                    if matches:
                        # 1. GENERACIÓN DE POWER-UPS
                        for match in matches:
                            match_length = len(match)
                            
                            if match_length >= 4:
                                
                                target_tile = tile1 if tile1 in match else tile2 if tile2 in match else match[0]
                                
                                
                                if match_length == 4:
                                    target_tile.is_line_clear = True
                                elif match_length >= 5:
                                    target_tile.is_color_bomb = True
                                    
                                
                                match.remove(target_tile)


                    self._calculate_matches([tile1, tile2])

                    

            Timer.tween(
                0.25,
                [
                    (tile1, {"x": target_orig_x, "y": target_orig_y}),
                    (tile2, {"x": orig_x, "y": orig_y}),
                ],
                on_finish=arrive,
            )
        else:
            if dx == 0 and dy == 0:
                tile1.x = orig_x
                tile1.y = orig_y
                
                if getattr(tile1, 'is_line_clear', False) or getattr(tile1, 'is_color_bomb', False):
                    self.active = False
                    self.board.matches.append([tile1])
                    self._calculate_matches([tile1])
                else:
                    self.active = True
            else:
                self.active = False
                Timer.tween(
                    0.2,
                    [(tile1, {"x": orig_x, "y": orig_y})],
                    on_finish=lambda: setattr(self, 'active', True)
                )

    def _calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if not matches:
            if not self.board.has_possible_matches():
                tweens = self.board.shuffle_tiles()
                Timer.tween(0.5, tweens, on_finish=lambda: setattr(self, 'active', True))
            else:
                self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        # INTERCEPCIÓN Y GENERACIÓN DE POWER-UPS
        for match in self.board.matches:
            match_length = len(match)
            if match_length >= 4:
               
                target_tile = next((t for t in tiles if t in match), match[0])

                if not getattr(target_tile, 'is_line_clear', False) and not getattr(target_tile, 'is_color_bomb', False):
                    if match_length == 4:
                        target_tile.is_line_clear = True
                    else:
                        target_tile.is_color_bomb = True
                    
                    match.remove(target_tile)

        # REACCIONES EN CADENA
        destroyed_coords = self.board.get_chain_destruction()

    
        self.score += len(destroyed_coords) * 50

        self.board.remove_matches(destroyed_coords)

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )