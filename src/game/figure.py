from enum import Enum
from abc import ABC

import pygame, os
from src.game.consts import *


class FigureType(Enum):
    KING = 1
    QUEEN = 2
    ROOK = 3
    BISHOP = 4
    KNIGHT = 5
    PAWN = 6


class Colors(Enum):
    WHITE = 1
    BLACK = 2


class Figure(ABC):
    # value of Figure is important for AI and taking decisions with min-max algorithm
    def __init__(self, type: FigureType, color: Colors, value: float) -> None:
        self.type = type
        self.color = color
        self.value = value
        # value_sign will be used for AI maybe to AI know which figures is mine
        self.moves = []
        self.moved = False
        self.image = os.path.join("images", f"{self.color}_{self.type}.png")
        self.image_rect = None

    def add_move(self, move) -> None:
        self.moves.append(move)

    def clear_moves(self) -> None:
        self.moves = []

    def image_with_size(
        self, screen: pygame.Surface, size: int, pos: tuple[int, int]
    ) -> None:
        image = pygame.image.load(self.image)
        image = pygame.transform.scale(image, (SQUARE_SIZE + size, SQUARE_SIZE + size))
        self.image_rect = image.get_rect(center=pos)
        screen.blit(image, self.image_rect)


class Pawn(Figure):

    def __init__(self, color: Colors) -> None:
        super().__init__(FigureType.PAWN, color, 1.0)
        self.dir = -1 if color == Colors.WHITE else 1
        # dir is for direction of the pawn white -> up black -> down
        # to know if the last move of the pawn was 2 squares
        self.en_passant = False


class Knight(Figure):

    def __init__(self, color: Colors) -> None:
        super().__init__(FigureType.KNIGHT, color, 3.0)


class Bishop(Figure):

    def __init__(self, color: Colors) -> None:
        super().__init__(
            FigureType.BISHOP, color, 3.001
        )  # this way if AI had to choose it will know that bishop is a little more important than knight


class Rook(Figure):

    def __init__(self, color: Colors) -> None:
        super().__init__(FigureType.ROOK, color, 5.0)


class Queen(Figure):

    def __init__(self, color: Colors) -> None:
        super().__init__(FigureType.QUEEN, color, 9.0)


class King(Figure):

    def __init__(self, color: Colors) -> None:
        super().__init__(FigureType.KING, color, 10000.0)
        self.right_rook = None  # need for castling
        self.left_rook = None
