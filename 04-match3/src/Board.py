"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self._is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        for match in self.matches:
            for tile in match:
                self.tiles[tile.i][tile.j] = None

        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def _is_match_at(self, i: int, j: int) -> bool:
        """Verificador puro sin efectos secundarios. No modifica la memoria del tablero."""
        tile_color = self.tiles[i][j].color
        
        # Revisión Horizontal
        count = 1
        for x in range(j - 1, -1, -1):
            if self.tiles[i][x].color == tile_color: count += 1
            else: break
        for x in range(j + 1, settings.BOARD_WIDTH):
            if self.tiles[i][x].color == tile_color: count += 1
            else: break
        if count >= 3: return True
        
        # Revisión Vertical
        count = 1
        for y in range(i - 1, -1, -1):
            if self.tiles[y][j].color == tile_color: count += 1
            else: break
        for y in range(i + 1, settings.BOARD_HEIGHT):
            if self.tiles[y][j].color == tile_color: count += 1
            else: break
        if count >= 3: return True
        
        return False

    def has_possible_matches(self) -> bool:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.tiles[i][j]
                
                # Simular derecha
                if j < settings.BOARD_WIDTH - 1:
                    right_tile = self.tiles[i][j + 1]
                    self.tiles[i][j], self.tiles[i][j + 1] = right_tile, tile
                    
                    is_match = self._is_match_at(i, j) or self._is_match_at(i, j + 1)
                    
                    self.tiles[i][j], self.tiles[i][j + 1] = tile, right_tile # Revertir
                    if is_match: return True

                # Simular abajo
                if i < settings.BOARD_HEIGHT - 1:
                    bottom_tile = self.tiles[i + 1][j]
                    self.tiles[i][j], self.tiles[i + 1][j] = bottom_tile, tile
                    
                    is_match = self._is_match_at(i, j) or self._is_match_at(i + 1, j)
                    
                    self.tiles[i][j], self.tiles[i + 1][j] = tile, bottom_tile # Revertir
                    if is_match: return True
        return False


    def shuffle_tiles(self) -> list:
        flat_tiles = [self.tiles[i][j] for i in range(settings.BOARD_HEIGHT) for j in range(settings.BOARD_WIDTH)]
        random.shuffle(flat_tiles)
        
        idx = 0
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                self.tiles[i][j] = flat_tiles[idx]
                self.tiles[i][j].i = i
                self.tiles[i][j].j = j
                idx += 1

        # Romper coincidencias activamente para evitar bucles infinitos
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                attempts = 0
                while self._is_match_at(i, j) and attempts < 20:
                    rand_i = random.randint(0, settings.BOARD_HEIGHT - 1)
                    rand_j = random.randint(0, settings.BOARD_WIDTH - 1)
                    
                    t1, t2 = self.tiles[i][j], self.tiles[rand_i][rand_j]
                    self.tiles[i][j], self.tiles[rand_i][rand_j] = t2, t1
                    t1.i, t1.j, t2.i, t2.j = rand_i, rand_j, i, j
                    attempts += 1

        if not self.has_possible_matches():
            return self.shuffle_tiles() # Recursividad de seguridad

        # Generar destinos para el tween
        tweens = []
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.tiles[i][j]
                tweens.append((tile, {"x": j * settings.TILE_SIZE, "y": i * settings.TILE_SIZE}))
        return tweens

    
    def get_chain_destruction(self) -> set:
        to_destroy = set()
        queue = []
        

        for match in self.matches:
            for tile in match:
                queue.append(tile)
                
        # Buscando efectos en cadena
        while queue:
            tile = queue.pop(0)
            
            if (tile.i, tile.j) in to_destroy:
                continue
                
            to_destroy.add((tile.i, tile.j))
            
            # Limpia-Líneas
            if getattr(tile, 'is_line_clear', False):
                for c in range(settings.BOARD_WIDTH):
                    t = self.tiles[tile.i][c]
                    if t is not None and (t.i, t.j) not in to_destroy:
                        queue.append(t)
                for r in range(settings.BOARD_HEIGHT):
                    t = self.tiles[r][tile.j]
                    if t is not None and (t.i, t.j) not in to_destroy:
                        queue.append(t)
                        
            # Bomba de Color
            elif getattr(tile, 'is_color_bomb', False):
                target_color = tile.color
                for r in range(settings.BOARD_HEIGHT):
                    for c in range(settings.BOARD_WIDTH):
                        t = self.tiles[r][c]
                        if t is not None and t.color == target_color and (t.i, t.j) not in to_destroy:
                            queue.append(t)
                            
        return to_destroy

    def remove_matches(self, destroyed_coords: set = None) -> None:

        if destroyed_coords is None:
            destroyed_coords = self.get_chain_destruction()
            
        for i, j in destroyed_coords:
            self.tiles[i][j] = None

        self.matches = []