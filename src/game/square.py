from src.game.figure import *


class Square:

    def __init__(self, row: int, col: int, figure: Figure | None = None) -> None:
        self.row = row
        self.col = col
        self.figure = figure

    def __eq__(self, other) -> bool:
        if not isinstance(other, Square):
            return False
        return self.row == other.row and self.col == other.col

    def has_figure(self) -> bool:
        return self.figure != None

    def has_opponent_figure(self, color: Colors) -> bool:
        return self.has_figure() and self.figure.color != color

    def has_team_figure(self, color: Colors) -> bool:
        return self.has_figure() and self.figure.color == color

    def is_empty(self) -> bool:
        return not self.has_figure()

    @staticmethod
    def in_range(*args) -> bool:
        for arg in args:
            if arg < 0 or arg > 7:
                return False
        return True
