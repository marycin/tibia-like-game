from dataclasses import dataclass
from typing import Tuple
from server.action_type import ActionType

@dataclass
class Action:
    type: ActionType
    field: Tuple[int, int]
    player_id: int = None  # <---- Dodajemy player_id

    @staticmethod
    def from_dict(data: dict) -> 'Action':
        try:
            return Action(
                field=tuple(data["field"]),
                type=ActionType(data["type"]),
                player_id=data.get("player_id")
            )
        except Exception:
            raise TypeError("Invalid data format")
