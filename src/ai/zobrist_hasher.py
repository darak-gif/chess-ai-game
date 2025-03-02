import random

from src.game.figure import *
from src.game.board import Board


class ZobristHasher:
    def __init__(self) -> None:
        self.table = {}
        random.seed(42)
        
        # Generate unique random numbers for (figure,color,pos(row,col))
        for row in range(ROWS):
            for col in range(COlS):
                for piece in FigureType:
                    for color in Colors:
                        self.table[(piece, color, row, col)] = random.getrandbits(
                            64
                        )  # 64-bites digit

    def hash_board(self, board: Board) -> int:

        board_hash = 0
        for row in range(ROWS):
            for col in range(COlS):
                if board.squares[row][col].has_figure():
                    fig = board.squares[row][col].figure
                    piece_key = (fig.type, fig.color, row, col)
                    board_hash ^= self.table[
                        piece_key
                    ]  # XOR for unique digit for this figure
        return board_hash
