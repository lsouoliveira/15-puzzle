from typing import Tuple
from .widget import Widget
from .input import Input
from .event import MouseEvent
from pygame.rect import Rect


class GUI:
    _root: Widget

    def __init__(self, root: Widget, viewport: Rect):
        self._root = root
        self._is_mouse_down = False
        self._viewport = viewport
        self._last_mouse_pos = self._relative_mouse_pos()

    def update(self):
        self._check_for_mouse_events()
        self._root.update()

    def draw(self, screen):
        self._root.draw(screen)

    @property
    def viewport(self) -> Rect:
        return self._viewport

    @viewport.setter
    def viewport(self, value: Rect):
        self._viewport = value

    def _check_for_mouse_events(self):
        mouse_pos = self._relative_mouse_pos()
        delta = (
            mouse_pos[0] - self._last_mouse_pos[0],
            mouse_pos[1] - self._last_mouse_pos[1],
        )

        if mouse_pos != self._last_mouse_pos:
            self._last_mouse_pos = mouse_pos

            self._root.notify("mousemove", MouseEvent(mouse_pos, delta))

        if self._can_click_start(mouse_pos):
            self._is_mouse_down = True

            if self._root.contains(mouse_pos):
                return self._root.notify("mousedown", MouseEvent(mouse_pos, delta))

        if self._can_click_end():
            self._is_mouse_down = False

            if self._root.contains(mouse_pos):
                self._root.notify("mouseup", MouseEvent(mouse_pos, delta))
                self._root.notify("click", MouseEvent(mouse_pos, delta))

    def _relative_mouse_pos(self) -> Tuple[int, int]:
        x, y = Input().mouse_pos()
        root_rect = self._root.rect
        vx, vy = self._viewport.x, self._viewport.y
        vw, vh = self._viewport.size
        rx, ry = (x - vx) / vw * root_rect.w, (y - vy) / vh * root_rect.h

        rx = int(max(0, min(rx, root_rect.width)))
        ry = int(max(0, min(ry, root_rect.height)))

        return (rx, ry)

    def _can_click_start(self, mouse_pos: Tuple[int, int]) -> bool:
        return (
            Input().is_mouse_button_down(0)
            and self._root.contains(mouse_pos)
            and not self._is_mouse_down
        )

    def _can_click_end(self) -> bool:
        return not Input().is_mouse_button_down(0) and self._is_mouse_down
