"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Room.
"""

import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

from gale.tilemap import TileMap

import settings
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Entity import Entity
from src.GameObject import GameObject
from src.states.entity.EntityIdleState import EntityIdleState
from src.states.entity.EntityWalkState import EntityWalkState
from src.world.Doorway import Doorway
from src.Projectile import Projectile


_ENEMY_TYPES = ["skeleton", "slime", "bat", "ghost", "spider"]

# Door archway detection zones, in the same room-local coordinates as
# every entity's x/y (not screen space, so this works regardless of
# camera/adjacent-room render offsets). Wider than the doorway's own
# get_collision_rect() on purpose -- these only decide *whether* the
# player is close enough to a doorway to bother clipping at all; the
# actual visible shape while crossing is the doorway's own, narrower,
# rect (see _doorway_opening_for below), applied with gale.stencil in
# Entity.render_sprite so the player is seen passing through the wall
# opening -- clipped by its edges -- instead of popping in and out of
# existence.
_DOORWAY_ZONES = {
    "left": pygame.Rect(
        -settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "right": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "top": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        -settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
    "bottom": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        settings.VIRTUAL_HEIGHT - settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
}


def _doorway_opening_for(
    rect: pygame.Rect, doorways_by_direction: dict
) -> Optional[pygame.Rect]:
    """
    :returns: The precise opening rect of whichever doorway rect is
        close to (i.e. overlapping the wider detection zone of), or
        None if rect isn't near any doorway right now.
    """
    for direction, zone in _DOORWAY_ZONES.items():
        if zone.colliderect(rect) and direction in doorways_by_direction:
            return doorways_by_direction[direction].get_collision_rect()

    return None


class Room:
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
        is_boss_room: bool = False,
        entry_direction: str = "bottom", 
    ) -> None:
        self.player = player
        self.on_game_over = on_game_over
        self.is_boss_room = is_boss_room
        self.chest = None

        self.width = settings.MAP_WIDTH
        self.height = settings.MAP_HEIGHT

        self.tilemap = TileMap(settings.TILE_SIZE, settings.TILE_SIZE, self.width, self.height)
        self.tilemap.add_tileset(settings.TILESET)
        self._generate_walls_and_floors()

        self.entities: List[Entity] = []
        self.objects: List[GameObject] = []

       
        if not self.is_boss_room:
            self._generate_entities()
            self._generate_objects()
            self.chest_spawned = False
            self.spawn_chest_randomly()
            
            self.doorways = [
                Doorway("top", False, self),
                Doorway("bottom", False, self),
                Doorway("left", False, self),
                Doorway("right", False, self),
            ]
        else:
           
            self._generate_boss_room_elements()
            
            # Creamos únicamente la puerta de entrada activa para que el gráfico y colisión coincidan
            doorway_in = Doorway(entry_direction, True, self)
            self.doorways = [doorway_in]

        self._doorways_by_direction = {
            doorway.direction: doorway for doorway in self.doorways
        }

        self.render_offset_x = settings.MAP_RENDER_OFFSET_X
        self.render_offset_y = settings.MAP_RENDER_OFFSET_Y

        self.adjacent_offset_x = 0
        self.adjacent_offset_y = 0

        self.projectiles: List[Any] = []

    def update(self, dt: float) -> None:
        # Don't update anything if we are sliding to another room.
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self.player.update(dt)

        for entity in self.entities:
            if entity.health <= 0:
                entity.dead = True


                if getattr(entity, "is_boss", False):
                    print("[LOG] 🏆 ¡VICTORIA! ¡Has derrotado al jefe final de la mazmorra!")
                    
                    if "victory" in settings.SOUNDS:
                        settings.SOUNDS["victory"].play()
                    else:
                        settings.SOUNDS["door"].play()
                    
                   
                    from gale.timer import Timer
                    Timer.after(3.0, lambda: setattr(self, "boss_defeated", True))


        
                # Chance to drop a heart.
                elif not entity.dropped and random.randint(1, 10) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["heart"], entity.x, entity.y)
                    )

                # Whether the entity dropped or not, it is assumed that it did.
                entity.dropped = True
            elif not entity.dead:
                if getattr(entity, "is_boss", False) and not entity.invulnerable_to_sword:
                    entity.vulnerability_timer -= dt
                    if entity.vulnerability_timer <= 0:
                        entity.invulnerable_to_sword = True
                        print("[LOG] El jefe ha recuperado su inmunidad a la espada.")


                if getattr(entity, "is_boss", False):
                    entity.fire_timer = getattr(entity, "fire_timer", 0.0) + dt
                    
                    
                    if entity.fire_timer >= 4.0:
                        entity.fire_timer = 0.0
                        
                        import math
                        
                        px = self.player.x + self.player.width / 2
                        py = self.player.y + self.player.height / 2
                        bx = entity.x + entity.width / 2
                        by = entity.y + entity.height / 2
                        
                        angle = math.atan2(py - by, px - bx)
                        fire_speed = 60.0
                        dx = math.cos(angle) * fire_speed
                        dy = math.sin(angle) * fire_speed
                        
                        fire_obj = GameObject(
                            {
                                "type": "fireball",
                                "texture": "fire",
                                "states": {"default": {"frame": 0}},
                                "width": 8,
                                "height": 8,
                                "solid": False,
                                "default_state": "default",
                            },
                            bx,
                            by
                        )
                        
                        fire_obj.dx = dx
                        fire_obj.dy = dy

                        fireball_proj = Projectile(obj=fire_obj, direction="none")
                        self.projectiles.append(fireball_proj)
                        
                        
                        print("[LOG] ☄️ ¡El jefe ha disparado una bola de fuego hacia el jugador!")

                entity.process_ai(self, dt)
                entity.update(dt)

            # Collision between the player and entities in the room.
            if (
                not entity.dead
                and self.player.collides(entity)
                and not self.player.invulnerable
            ):
                settings.SOUNDS["hit-player"].play()
                if getattr(entity, "is_boss", False):
                    self.player.damage(2) 
                else:
                    self.player.damage(1)
                self.player.go_invulnerable(1.5)

                if self.player.health == 0:
                    self.on_game_over()

        self.entities = [entity for entity in self.entities if not entity.dead]

        for obj in list(self.objects):
            obj.update(dt)

            if self.player.collides(obj):
                obj.on_collide()

                if obj.solid and not obj.taken:
                    self._push_player_out_of(obj)

                if obj.consumable:
                    obj.on_consume(self.player, obj)
                    self.objects.remove(obj)

        for projectile in list(self.projectiles):
            projectile.update(dt)

            if projectile.dead:
                if projectile in self.projectiles:
                    self.projectiles.remove(projectile)
                continue

            # Colisión con el jugador (ÚNICAMENTE si es una bola de fuego del jefe)
            if getattr(projectile.obj, "type", "") == "fireball":
                if projectile.collides(self.player):
                    settings.SOUNDS["hit-player"].play()
                    print("[LOG] 💀 ¡Una bola de fuego alcanzó al jugador!")
                    self.player.health = 0  
                    self.on_game_over()
                    projectile.dead = True

            # Colisión con entidades (Enemigos normales o el Jefe -> Flechas del jugador)
            if not projectile.dead:
                for entity in self.entities:
                    if not entity.dead and projectile.collides(entity):
                       
                        if getattr(projectile.obj, "type", "") == "fireball":
                            continue

                        projectile.dead = True

                        if getattr(entity, "is_boss", False):
                            
                            entity.invulnerable_to_sword = False
                            entity.vulnerability_timer = 3.0
                            settings.SOUNDS["hit-enemy"].play()
                            print("[LOG] ¡El jefe es VULNERABLE a la espada!")
                        else:
                            # --- ENEMIGO NORMAL ---
                            entity.damage(1)
                            settings.SOUNDS["hit-enemy"].play()
                            print(f"[LOG] 🏹 ¡Flecha impactó a enemigo! Vida restante: {entity.health}")

                        break  

            
            if projectile.dead and projectile in self.projectiles:
                self.projectiles.remove(projectile)



    def _push_player_out_of(self, obj: GameObject) -> None:
        player = self.player
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_right = player.x + player.width
        player_bottom = player_y + player_height

        if (
            player.direction == "left"
            and not (player_y >= (obj.y + obj.height))
            and not (player_bottom <= obj.y)
        ):
            player.x = obj.x + obj.width
        elif (
            player.direction == "right"
            and not (player_y >= (obj.y + obj.height))
            and not (player_bottom <= obj.y)
        ):
            player.x = obj.x - player.width
        elif (
            player.direction == "down"
            and not (player.x >= (obj.x + obj.width))
            and not (player_right <= obj.x)
        ):
            player.y = obj.y - player.height
        elif (
            player.direction == "up"
            and not (player.x >= (obj.x + obj.width))
            and not (player_right <= obj.x)
        ):
            player.y = obj.y + obj.height - player.height / 2

    def take_adjacent_pot(self, player: TypeVar("Player")) -> None:
        """
        Looks for a takeable object directly in front of the player (one
        tile away, in the direction they're currently facing) and, if
        found, removes it from the room and has the player lift it.
        """
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_col = int((player.x + player.width / 2) // settings.TILE_SIZE)
        player_row = int((player_y + player_height / 2) // settings.TILE_SIZE)

        for obj in self.objects:
            if not obj.takeable:
                continue

            obj_col = int((obj.x + obj.width / 2) // settings.TILE_SIZE)
            obj_row = int((obj.y + obj.height / 2) // settings.TILE_SIZE)

            adjacent = (
                (player.direction == "right" and obj_row == player_row and obj_col == player_col + 1)
                or (player.direction == "left" and obj_row == player_row and obj_col == player_col - 1)
                or (player.direction == "up" and obj_col == player_col and obj_row == player_row - 1)
                or (player.direction == "down" and obj_col == player_col and obj_row == player_row + 1)
            )

            if adjacent:
                self.objects.remove(obj)
                player.change_state("pot-lift", pot=obj)
                return

    def _generate_walls_and_floors(self) -> None:
        """
        Generates the walls and floors of the room, randomizing the various
        varieties of said tiles for visual variety.
        """
        floor = self.tilemap.add_layer("floor")

        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                if x == 1 and y == 1:
                    tile_id = settings.TILE_TOP_LEFT_CORNER
                elif x == 1 and y == self.height:
                    tile_id = settings.TILE_BOTTOM_LEFT_CORNER
                elif x == self.width and y == 1:
                    tile_id = settings.TILE_TOP_RIGHT_CORNER
                elif x == self.width and y == self.height:
                    tile_id = settings.TILE_BOTTOM_RIGHT_CORNER
                elif x == 1:
                    tile_id = random.choice(settings.TILE_LEFT_WALLS)
                elif x == self.width:
                    tile_id = random.choice(settings.TILE_RIGHT_WALLS)
                elif y == 1:
                    tile_id = random.choice(settings.TILE_TOP_WALLS)
                elif y == self.height:
                    tile_id = random.choice(settings.TILE_BOTTOM_WALLS)
                else:
                    tile_id = random.choice(settings.TILE_FLOORS)

                floor[y - 1][x - 1] = tile_id

    def _generate_entities(self) -> None:
        """Randomly creates an assortment of enemies for the player to fight."""
        for _ in range(10):
            enemy_type = random.choice(_ENEMY_TYPES)
            definition = ENTITY_DEFS[enemy_type]

            entity = Entity(
                x=random.randint(
                    settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                    settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - 16,
                ),
                y=random.randint(
                    settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                    settings.MAP_HEIGHT * settings.TILE_SIZE
                    + settings.MAP_RENDER_OFFSET_Y
                    - settings.TILE_SIZE
                    - 16,
                ),
                width=16,
                height=16,
                walk_speed=definition.get("walk_speed", 20),
                health=1,
                animation_defs=definition["animations"],
                states={},
            )

            entity.state_machine.states = {
                "walk": lambda sm, e=entity: EntityWalkState(e, sm),
                "idle": lambda sm, e=entity: EntityIdleState(e, sm),
            }
            entity.change_state("walk")
            self.entities.append(entity)

    def spawn_chest_randomly(self) -> None:
        """Genera el cofre de forma aleatoria y única en el calabozo."""
        if not hasattr(settings, "CHEST_SPAWNED_GLOBALLY"):
            settings.CHEST_SPAWNED_GLOBALLY = False

        if not settings.CHEST_SPAWNED_GLOBALLY and random.randint(1, 5) == 1:
            chest_x = random.randint(
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 2,
                settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 3 - 16,
            )
            chest_y = random.randint(
                settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2,
                settings.MAP_HEIGHT * settings.TILE_SIZE
                + settings.MAP_RENDER_OFFSET_Y
                - settings.TILE_SIZE * 3
                - 16,
            )
            
            chest = GameObject(GAME_OBJECT_DEFS["chest"], chest_x, chest_y)
            
            def open_chest() -> None:
                if chest.state == "closed" and not getattr(self.player, "has_bow", False):
                    chest.state = "open"
                    chest.solid = False
                    self.player.has_bow = True
                    print("¡Has encontrado un arco!")

            chest.on_collide = open_chest
            self.objects.append(chest)
            settings.CHEST_SPAWNED_GLOBALLY = True
            self.chest_spawned = True
    def _generate_boss_room_elements(self) -> None:
        """Configura la sala del jefe: sin enemigos ni vasijas, solo al jefe en el lado opuesto."""
        # Aquí instanciaremos al jefe en la parte superior/central opuesta a la entrada
        from src.Entity import Entity
        from src.definitions.entity import ENTITY_DEFS
        from src.states.entity.EntityIdleState import EntityIdleState
        from src.states.entity.EntityWalkState import EntityWalkState

        
        boss_x = settings.VIRTUAL_WIDTH // 2 - 8
        boss_y = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2

        
        definition = ENTITY_DEFS.get("ghost", ENTITY_DEFS["skeleton"])
        
        boss = Entity(
            x=boss_x,
            y=boss_y,
            width=16,
            height=16,
            walk_speed=20,
            health=6,  # Vida inicial del jefe
            animation_defs=definition["animations"],
            states={},
        )
        
        boss.is_boss = True
        boss.invulnerable_to_sword = True
        boss.vulnerability_timer = 0.0


        boss.state_machine.states = {
            "walk": lambda sm, e=boss: EntityWalkState(e, sm),
            "idle": lambda sm, e=boss: EntityIdleState(e, sm),
        }
        boss.change_state("idle")
        
        self.entities.append(boss)
        print("[LOG] ¡Habitación del Jefe generada con éxito!")
            
    def _generate_objects(self) -> None:
        """Randomly creates an assortment of obstacles for the player to navigate around."""
        if not hasattr(settings, "CHEST_SPAWNED_GLOBALLY"):
            settings.CHEST_SPAWNED_GLOBALLY = False

   
        if not settings.CHEST_SPAWNED_GLOBALLY and random.randint(1, 5) == 1:
            chest_x = random.randint(
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 2,
                settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 3 - 16,
            )
            chest_y = random.randint(
                settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2,
                settings.MAP_HEIGHT * settings.TILE_SIZE
                + settings.MAP_RENDER_OFFSET_Y
                - settings.TILE_SIZE * 3
                - 16,
            )
            
            chest = GameObject(GAME_OBJECT_DEFS["chest"], chest_x, chest_y)
            
            # Lógica de interacción al colisionar/abrir el cofre
            def open_chest() -> None:
                if chest.state == "closed" and not getattr(self.player, "has_bow", False):
                    chest.state = "open"
                    chest.solid = False 
                    self.player.has_bow = True
                    print(f"[LOG] ¡El jugador ha tomado el arco desde el cofre en ({chest_x}, {chest_y})!")

                
                    bow_item = GameObject(GAME_OBJECT_DEFS["bow_item"], chest_x, chest_y - 10)
                    self.objects.append(bow_item)
                    print("¡Has encontrado un arco!")

            chest.on_collide = open_chest
            self.objects.append(chest)
            settings.CHEST_SPAWNED_GLOBALLY = True

       
        switch = GameObject(
            GAME_OBJECT_DEFS["switch"],
            random.randint(
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - 16,
            ),
            random.randint(
                settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                settings.MAP_HEIGHT * settings.TILE_SIZE
                + settings.MAP_RENDER_OFFSET_Y
                - settings.TILE_SIZE
                - 16,
            ),
        )
        self.objects.append(switch)

        def open_all_doors() -> None:
            if switch.state == "unpressed":
                switch.state = "pressed"

                for doorway in self.doorways:
                    doorway.open = True

                settings.SOUNDS["door"].play()

        switch.on_collide = open_all_doors

        for y in range(2, self.height):
            for x in range(2, self.width):
                if random.randint(1, 20) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["pot"], x * 16, y * 16)
                    )

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        offset_x = self.adjacent_offset_x + camera_offset_x
        offset_y = self.adjacent_offset_y + camera_offset_y

        # Not tilemap.render(surface): offset_x/offset_y can carry the room
        # a full VIRTUAL_WIDTH/HEIGHT off-screen mid room-shift, and
        # Surface.subsurface() (used for 07-ultimate_fantasy's BattleState,
        # whose offset is fixed and always in-bounds) requires the rect to
        # land fully inside surface -- a plain blit per tile, sourcing the
        # gid/rect from the TileMap/Tileset instead of the old self.tiles
        # list and settings.frame("tiles", ...), has no such restriction.
        for y in range(self.height):
            for x in range(self.width):
                gid = self.tilemap.get_gid("floor", y, x)
                tileset = self.tilemap.tileset_for_gid(gid)
                surface.blit(
                    tileset.image,
                    (
                        x * settings.TILE_SIZE + self.render_offset_x + offset_x,
                        y * settings.TILE_SIZE + self.render_offset_y + offset_y,
                    ),
                    tileset.rect_for(gid),
                )

        for doorway in self.doorways:
            doorway.render(surface, offset_x, offset_y)

        for obj in self.objects:
            obj.render(surface, offset_x, offset_y)

        for entity in self.entities:
            if not entity.dead:
                entity.render(surface, offset_x, offset_y)

        # The player and projectiles are drawn using only the camera pan —
        # never this room's own adjacent_offset — matching the original,
        # where Player:render()/Projectile:render() take no room offset at
        # all. Their x/y already track the correct absolute (pre-camera-pan)
        # screen position on their own, including mid-tween during a room
        # shift; adding adjacent_offset on top (as tiles/entities do) would
        # draw them a full room-width off from where they actually are.
        #
        # While the player is near a doorway, clip their sprite to that
        # doorway's own opening rect (via gale.stencil, applied inside
        # Entity.render_sprite) instead of hiding them outright: the part
        # of the sprite still overlapping solid wall disappears, but the
        # part inside the opening keeps showing, so walking (or, mid
        # room-shift, tweening) through the gap reads as passing under/
        # through the archway rather than blinking out of existence.
        if self.player:
            self.player.visibility_clip_rect = _doorway_opening_for(
                self.player.get_collision_rect(), self._doorways_by_direction
            )
            self.player.render(surface, camera_offset_x, camera_offset_y)
            self.player.visibility_clip_rect = None

        for projectile in self.projectiles:
            if not self.is_boss_room and _doorway_opening_for(
                projectile.get_collision_rect(), self._doorways_by_direction
            ):
                pass
            else:
                projectile.render(surface, camera_offset_x, camera_offset_y)

       
