import pygame
import settings
import random

from src.LogPair import LogPair

class NormalMode:
    can_spawn_powerups = False

    def update_bird_position(self, bird, dt) -> None:
        bird.vy += settings.GRAVITY * dt
        bird.y += bird.vy * dt

    def handle_bird_input(self, bird, input_id, input_data) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.vy = -settings.JUMP_TAKEOFF_SPEED
            settings.SOUNDS["jump"].play()

    def get_log_spawn_timer(self) -> float:
        return settings.TIME_TO_SPAWN_LOGS

    def generate_log_pair(self, x: float, last_y: float) -> LogPair:
        y = max(
            -settings.LOG_HEIGHT + 30,
            min(
                last_y + random.randint(-40, 40),
                settings.VIRTUAL_HEIGHT - 120 - settings.LOG_HEIGHT,
            ),
        )
        return LogPair(x, y)


class HardMode:
    can_spawn_powerups = True

    def update_bird_position(self, bird, dt) -> None:
        bird.vy += settings.GRAVITY * dt
        bird.y += bird.vy * dt
        bird.x += bird.vx * dt
        bird.x = max(0, min(bird.x, settings.VIRTUAL_WIDTH - bird.width))


    def handle_bird_input(self, bird, input_id, input_data) -> None:
        if input_id == "jump" and input_data.pressed:
            settings.SOUNDS["jump"].play()
            bird.vy = -settings.JUMP_TAKEOFF_SPEED

        if input_id == "left":
            if input_data.pressed:
                bird.vx = -settings.HORIZONTAL_SPEED
            elif input_data.released and bird.vx < 0:
                bird.vx = 0

        elif input_id == "right":
            if input_data.pressed:
                bird.vx = settings.HORIZONTAL_SPEED
            elif input_data.released and bird.vx > 0:
                bird.vx = 0


    def get_log_spawn_timer(self) -> float:
         return random.uniform(1.2, 2.2)

    def generate_log_pair(self, x: float, last_y: float) -> LogPair:

        gap = random.randint(70, 110)
        y = max(
                    -settings.LOG_HEIGHT + 40,
                    min(
                        last_y + random.randint(-40, 40),
                        settings.VIRTUAL_HEIGHT - 30 - settings.LOG_HEIGHT,
                    ),
                )

        is_moving = random.random() < 0.5

        log_pair = LogPair(x, y, gap, is_moving)


        return log_pair