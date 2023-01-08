from typing import Tuple
import pygame


class Input:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Input, cls).__new__(cls)

        return cls.instance

    def is_mouse_button_down(self, button: int) -> bool:
        return pygame.mouse.get_pressed(3)[button]

    def mouse_pos(self) -> Tuple[int, int]:
        return pygame.mouse.get_pos()
