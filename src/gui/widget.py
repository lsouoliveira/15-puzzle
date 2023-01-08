from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from os import wait
from typing import Optional, Tuple
from pygame import Rect

from .event import Event


class Widget(ABC):
    _parent: Optional[Widget]

    def __init__(self, rect=None, parent=None):
        self._events = {}
        self._rect = rect or Rect(0, 0, 0, 0)
        self._parent = None

        if parent:
            parent.add_widget(self)

    @property
    def parent(self) -> Optional[Widget]:
        return self._parent

    @parent.setter
    def parent(self, widget: Widget):
        self._parent = widget

    def root(self) -> Optional[Widget]:
        parent = self._parent
        child = self

        while parent:
            child = parent
            parent = child.parent

        return child

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def draw(self, screen):
        pass

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, r: Rect):
        self._rect = r

    def contains(self, position: Tuple[int, int]) -> bool:
        x, y = self._rect.x, self._rect.y
        w, h = self._rect.size
        px, py = position

        return px >= x and px <= x + w and py >= y and py <= y + h

    def connect(self, event_name: str, callback: Callable):
        if not event_name in self._events:
            self._events[event_name] = []

        self._events[event_name] += [callback]

    def notify(self, event_name: str, event_data: Event):
        if not event_name in self._events:
            return

        for event in self._events[event_name]:
            event(event_data)
