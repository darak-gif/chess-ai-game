import pygame
from src.game.consts import *
from src.game.figure import *


class Dragger:

    def __init__(self) -> None:
        self.pos_x = 0
        self.pos_y = 0
        self.original_col = 0
        self.original_row = 0
        self.figure = None
        self.is_dragging = False

    def update_screen(self, screen: pygame.Surface) -> None:
        if self.figure != None:
            self.figure.image_with_size(screen, 30, (self.pos_x, self.pos_y))

    def update_pos(self, new_pos: tuple[int, int]) -> None:
        self.pos_x, self.pos_y = new_pos

    def save_original_pos(self, original_pos: tuple[int, int]) -> None:
        self.original_row = original_pos[1] // SQUARE_SIZE
        self.original_col = original_pos[0] // SQUARE_SIZE

    def save_dragged_figure(self, figure: Figure) -> None:
        self.figure = figure
        self.is_dragging = True

    def undragg_figure(self) -> None:
        self.figure = None
        self.is_dragging = False
