import pygame
import random
import sys
from PIL import ImageColor
from pygame.rect import Rect

from .gui.core import GUI
from .gui.view import View
from .gui.puzzle_grid import PuzzleGrid
from .gui.theme import Theme, Style


def hex_to_rgb(s):
    return ImageColor.getcolor(s, "RGB")


DEFAULT_STYLE = {
    "TILE_BG": hex_to_rgb("#3282B8"),
    "TILE_LABEL_COLOR": (255, 255, 255),
    "TILE_LABEL_TEXT_SIZE": 24,
    "PUZZLE_GRID_BG": hex_to_rgb("#1B262C"),
}


class Game:
    def _setup_pygame(self):
        pygame.init()
        pygame.font.init()

        self._screen = pygame.display.set_mode((400, 400), pygame.RESIZABLE)
        self._buffer = self._screen.copy()

        pygame.display.set_caption("15-puzzle")

        self._clock = pygame.time.Clock()

    def _main_loop(self):
        while True:
            self._update()
            self._draw()

    def _update(self):
        self._process_events()
        self._gui.update()
        self._clock.tick(60)

    def _process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                self._screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

                x, y = self._scaled_buffer_position
                _, h = self._screen.get_rect().size

                self._gui.viewport = Rect(x, y, h, h)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif (
                    pygame.key.get_mods() & pygame.KMOD_CTRL
                    and event.key == pygame.K_SPACE
                ):
                    self._shuffle_puzzle_grid()

    def _draw(self):
        self._buffer.fill((0, 0, 0))
        self._screen.fill(DEFAULT_STYLE["PUZZLE_GRID_BG"])
        self._gui.draw(self._buffer)
        self._draw_buffer()

        pygame.display.flip()

    def _shuffle_puzzle_grid(self):
        tiles_order = [i for i in range(16)]

        random.shuffle(tiles_order)

        self._puzzle_grid.tiles_ordering(tiles_order)

    @property
    def _scaled_buffer_position(self):
        screen_rect = self._screen.get_rect()

        screen_width = screen_rect.width
        screen_height = screen_rect.height

        return (screen_width / 2 - screen_height / 2, 0)

    def _scaled_buffer(self):
        screen_rect = self._screen.get_rect()
        screen_height = screen_rect.height

        return pygame.transform.scale(self._buffer, (screen_height, screen_height))

    def _draw_buffer(self):
        self._screen.blit(self._scaled_buffer(), self._scaled_buffer_position)

    def _setup_gui(self):
        self._view = View(Rect(0, 0, 400, 400))

        self._puzzle_grid = PuzzleGrid(Rect(0, 0, 400, 400), parent=self._view)
        self._puzzle_grid.tiles_ordering([i for i in range(16)])

        self._gui = GUI(root=self._view, viewport=Rect(0, 0, 400, 400))

        self._shuffle_puzzle_grid()

    def _setup_theme(self):
        Theme().use(Style.from_dict(DEFAULT_STYLE))

    def run(self) -> None:
        self._setup_theme()
        self._setup_pygame()
        self._setup_gui()
        self._main_loop()
