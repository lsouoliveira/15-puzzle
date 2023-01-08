from typing import Tuple


class Event:
    pass


class MouseEvent(Event):
    _position: Tuple[int, int]
    _delta: Tuple[int, int]

    def __init__(self, position: Tuple[int, int], delta: Tuple[int, int]):
        self._position = position
        self._delta = delta

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @property
    def delta(self) -> Tuple[int, int]:
        return self._delta
