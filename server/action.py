from dataclasses import dataclass
from typing import Tuple
from action_type import ActionType

@dataclass
class Action:
    type: ActionType
    field: Tuple[int, int]

    @staticmethod
    def from_dict(data: dict) -> 'Action':
        try:
            return Action(
            field=data["field"],
            type=ActionType(data["type"])
        )
        except Exception:
            raise TypeError("Invalid data format")
