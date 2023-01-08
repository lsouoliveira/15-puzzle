from __future__ import annotations

import pygame
import math
from pygame import Rect
from typing import Optional, Tuple, List

from .widget import Widget
from .theme import Theme
from .view import View
from .input import Input
from .event import MouseEvent


def dist_between_rects(r1, r2):
    return math.hypot(r1.x - r2.x, r1.y - r2.y)


def dir_between_rects(r1, r2):
    magnitude = dist_between_rects(r1, r2)

    return ((r1.x - r2.x) / magnitude, (r1.y - r2.y) / magnitude)


class Tile(Widget):
    def __init__(self, value: int, rect=None):
        super().__init__(rect)

        self._value = value
        self._font = pygame.font.Font(
            "data/fonts/8bit16.ttf", self._tile_label_text_size
        )
        self._show = True

    def show(self):
        self._show = True

    def hide(self):
        self._show = False

    @property
    def value(self) -> int:
        return self._value

    def update(self):
        return super().update()

    def draw(self, screen):
        if not self._show:
            return

        self._draw_bg(screen)
        self._draw_label(screen)

    @property
    def _tile_bg(self):
        return Theme().style.get_attr("TILE_BG")

    @property
    def _tile_label_color(self):
        return Theme().style.get_attr("TILE_LABEL_COLOR")

    @property
    def _tile_label_text_size(self):
        return Theme().style.get_attr("TILE_LABEL_TEXT_SIZE")

    def _draw_bg(self, screen):
        pygame.draw.rect(screen, self._tile_bg, self.rect, 0, 12)

    def _draw_label(self, screen):
        img = self._font.render(str(self._value), False, self._tile_label_color)

        img_rect = img.get_rect()
        img_rect.x = int(self.rect.x + self.rect.width / 2 - img_rect.width / 2)
        img_rect.y = int(self.rect.y + self.rect.height / 2 - img_rect.height / 2)

        screen.blit(img, img_rect)


class PuzzleGrid(View):
    def __init__(self, rect=None, parent=None):
        if not parent:
            raise ValueError("Parent should not be None")

        super().__init__(rect, parent)

        self._tile_drag_and_drop = None
        self._border_width = 8

        self.root().connect("mousemove", self._on_root_mousemove)
        self.root().connect("mouseup", self._on_root_mouseup)

    def draw(self, screen):
        self._draw_bg(screen)

        super().draw(screen)

    def update(self):
        super().update()

    def tiles_ordering(self, tiles_ordering: List[int]):
        if sorted(tiles_ordering) != [i for i in range(16)]:
            raise ValueError("Invalid ordering")

        self._create_tiles(tiles_ordering)
        self._update_layout()

    def tiles_count(self) -> int:
        return len(self._tiles)

    def tile_at_matrix_index(self, index: Tuple[int, int]) -> Tile:
        x, y = index

        return self._tiles[y * 4 + x]

    def swap_tiles(self, a: Tile, b: Tile):
        a_index = self._tiles.index(a)
        b_index = self._tiles.index(b)

        self._tiles[a_index], self._tiles[b_index] = b, a
        self._update_layout()

    def get_tile_matrix_index(self, tile: Widget) -> Tuple[int, int]:
        tile_index = self._tiles.index(tile)

        return (tile_index % 4, tile_index // 4)

    def empty_tile(self) -> Optional[Tile]:
        for tile in self._tiles:
            if tile.value == 0:
                return tile

        return None

    def _on_root_mousemove(self, e: MouseEvent):
        if self._tile_drag_and_drop:
            self._tile_drag_and_drop.on_mousemove(e)

    def _on_root_mouseup(self, e: MouseEvent):
        if self._tile_drag_and_drop:
            self._tile_drag_and_drop.on_mouseup(e)

            self._tile_drag_and_drop = None

    def _create_tiles(self, tiles_ordering: List[int]):
        self._tiles = []

        for i in range(len(self.widgets)):
            self.widgets.pop(0)

        for i in tiles_ordering:
            tile = Tile(i)

            if tile.value == 0:
                tile.hide()

            tile.connect(
                "mousedown", lambda e, tile=tile: self._on_tile_mousedown(e, tile)
            )

            self.add_widget(tile)
            self._tiles.append(tile)

    def _on_tile_mousedown(self, _: MouseEvent, tile: Tile):
        if not self._tile_drag_and_drop and self._can_tile_be_moved(tile):
            self._tile_drag_and_drop = TileDragAndDrop(self, tile, self.empty_tile())

    def _can_tile_be_moved(self, tile: Tile) -> bool:
        if tile.value == 0:
            return False

        x, y = self.get_tile_matrix_index(tile)

        neighbours = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]

        for neighbour in neighbours:
            x, y = neighbour
            is_position_valid = x >= 0 and x < 4 and y >= 0 and y < 4

            if is_position_valid and self.tile_at_matrix_index(neighbour).value == 0:
                return True

        return False

    def _update_layout(self):
        for i in range(4):
            for j in range(4):
                tile = self._tiles[i * 4 + j]

                tile.rect.x = (
                    int((self._tile_width + self._border_width) * j)
                    + self._border_width
                )
                tile.rect.y = (
                    int((self._tile_height + self._border_width) * i)
                    + self._border_width
                )
                tile.rect.width = int(self._tile_width)
                tile.rect.height = int(self._tile_height)

    @property
    def _tile_width(self) -> float:
        return (self.rect.width - self._border_width * 5) / 4

    @property
    def _tile_height(self) -> float:
        return (self.rect.height - self._border_width * 5) / 4

    @property
    def _puzzle_grid_bg(self):
        return Theme().style.get_attr("PUZZLE_GRID_BG")

    def _draw_bg(self, screen):
        pygame.draw.rect(screen, self._puzzle_grid_bg, self.rect)


class TileDragAndDrop:
    _tmp_tile: Tile
    _target_dir: Tuple[int, int]

    def __init__(self, grid: PuzzleGrid, start_tile: Tile, end_tile: Tile):
        self._grid = grid
        self._start_tile = start_tile
        self._end_tile = end_tile
        self._start_distance = dist_between_rects(start_tile.rect, end_tile.rect)

        self._setup_tiles()

    def on_mouseup(self, e: MouseEvent):
        if self._can_swap(e.position[0], e.position[1]):
            self._grid.swap_tiles(self._start_tile, self._end_tile)

        self._start_tile.show()
        self._grid.remove_widget(self._tmp_tile)

    def on_mousemove(self, e: MouseEvent):
        self._tmp_tile.rect.x += e.delta[0] * abs(self._target_dir[0])
        self._tmp_tile.rect.y += e.delta[1] * abs(self._target_dir[1])

        self._clamp_tile_position(self._tmp_tile)

    def _can_swap(self, x, y):
        dir_x, dir_y = self._target_dir
        end_tile_rect = self._end_tile.rect

        return (
            (dir_x < 0 and x <= end_tile_rect.x + end_tile_rect.w)
            or (dir_x > 0 and x >= end_tile_rect.x)
            or (dir_y > 0 and y >= end_tile_rect.y)
            or (dir_y < 0 and y <= end_tile_rect.y + end_tile_rect.h)
        )

    def _clamp_tile_position(self, tile):
        dir_x, dir_y = self._target_dir
        tile_rect = tile.rect
        start_rect = self._start_tile.rect
        end_rect = self._end_tile.rect

        if dir_x < 0 or dir_x > 0:
            a, b = None, None

            if dir_x < 0:
                a, b = end_rect, start_rect
            else:
                a, b = start_rect, end_rect

            if tile_rect.x < a.x:
                tile_rect.x = a.x
            elif tile_rect.x + tile_rect.w > b.x + b.w:
                tile_rect.x = b.x

        if dir_y < 0 or dir_y > 0:
            a, b = None, None

            if dir_y < 0:
                a, b = end_rect, start_rect
            else:
                a, b = start_rect, end_rect

            if tile_rect.y < a.y:
                tile_rect.y = a.y
            elif tile_rect.y + tile_rect.w > b.y + b.w:
                tile_rect.y = b.y

    def _setup_tiles(self):
        self._target_dir = self._create_target_dir()
        self._tmp_tile = self._create_tmp_tile()

        self._start_tile.hide()
        self._grid.add_widget(self._tmp_tile)

    def _create_target_dir(self):
        start_tile_matrix_index = self._grid.get_tile_matrix_index(self._start_tile)
        end_tile_matrix_index = self._grid.get_tile_matrix_index(self._end_tile)

        return (
            end_tile_matrix_index[0] - start_tile_matrix_index[0],
            end_tile_matrix_index[1] - start_tile_matrix_index[1],
        )

    def _create_tmp_tile(self):
        tile_rect = self._start_tile.rect

        return Tile(
            self._start_tile.value,
            Rect(tile_rect.x, tile_rect.y, tile_rect.w, tile_rect.h),
        )
