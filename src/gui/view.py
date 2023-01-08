from typing import List, Tuple, Optional

from .widget import Widget
from .event import Event, MouseEvent


class View(Widget):
    _widgets: List[Widget]

    def __init__(self, rect=None, parent=None):
        super().__init__(rect, parent)

        self._widgets = []

        self.connect("click", self._handle_click)
        self.connect("mousedown", self._handle_mousedown)
        self.connect("mouseup", self._handle_mouseup)
        self.connect("mousemove", self._handle_mousemove)

    def add_widget(self, widget: Widget):
        if widget.parent:
            raise ValueError("Widget already has a parent")

        self._widgets.append(widget)
        widget.parent = self

    def remove_widget(self, widget: Widget):
        self._widgets.remove(widget)

    @property
    def widgets(self) -> List[Widget]:
        return self._widgets

    def update(self):
        for widget in self._widgets:
            widget.update()

    def draw(self, screen):
        for widget in self._widgets:
            widget.draw(screen)

    def _handle_click(self, e: MouseEvent):
        self._notify_widget_at_position(e.position, "click", e)

    def _handle_mousedown(self, e: MouseEvent):
        self._notify_widget_at_position(e.position, "mousedown", e)

    def _handle_mouseup(self, e: MouseEvent):
        self._notify_widget_at_position(e.position, "mouseup", e)

    def _handle_mousemove(self, e: MouseEvent):
        self._notify_widget_at_position(e.position, "mousemove", e)

    def _notify_widget_at_position(
        self, position: Tuple[int, int], event_name: str, event: Event
    ):
        widget = self._widget_at_position(position)

        if widget:
            widget.notify(event_name, event)

    def _widget_at_position(self, position: Tuple[int, int]) -> Optional[Widget]:
        for widget in self._widgets:
            if widget.contains(position):
                return widget

        return None
