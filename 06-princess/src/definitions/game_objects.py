"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition for game objects.
"""

from typing import Any, Dict

import settings
CHEST_STATE_CLOSED = 'closed'
CHEST_STATE_OPEN = 'open'

def _pickup_heart(player, obj) -> None:
    player.heal(2)
    settings.SOUNDS["heart-taken"].play()


GAME_OBJECT_DEFS: Dict[str, Dict[str, Any]] = {
    "switch": {
        "type": "switch",
        "texture": "switches",
        "frame": 2,
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "unpressed",
        "states": {
            "unpressed": {"frame": 2},
            "pressed": {"frame": 1},
        },
    },
    "pot": {
        "type": "pot",
        "texture": "tiles",
        "frame": 16,
        "width": 16,
        "height": 16,
        "solid": True,
        "consumable": False,
        "default_state": "default",
        "takeable": True,
        "states": {
            "default": {"frame": 16},
        },
    },
    # Definition of heart as a consumable object type.
    "heart": {
        "type": "heart",
        "texture": "hearts",
        "frame": 5,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": True,
        "default_state": "default",
        "states": {
            "default": {"frame": 5},
        },
        "on_consume": _pickup_heart,
    },
    "chest": {
        "type": "chest",
        "texture": "chest",
        "states": {
            "closed": {
                "frame": 0,
            },
            "open": {
                "frame": 0,
                "texture": "chest-open",
            },
        },
        "width": 16,
        "height": 16,
        "solid": True,
        "default_state": "closed",
    },
    "bow_item": {
        "type": "bow_item",
        "texture": "bow",
        "states": {
            "default": {
                "frame": 0,
            }
        },
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "default",
        "consumable": True,
        "on_consume": lambda player, obj: setattr(player, "has_bow", True),
    },
}
