import math, copy
from enum import Enum
from src.game.board import Board
from src.game.move import Move
from src.game.figure import *
from src.ai.zobrist_hasher import ZobristHasher


class AIType(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class AI:
    def __init__(self, type: AIType, color: Colors) -> None:
        self.type = type
        self.depth = 2 if type == AIType.EASY else 4 if type == AIType.MEDIUM else 6
        self.color = color
        self.points = (
            1000 if type == AIType.EASY else 1200 if type == AIType.MEDIUM else 1400
        )
        self.curr_board = None
        self.transposition_table = {}
        self.hasher = ZobristHasher()

    def evaluate_board(self) -> float:  # calculate how the game unfolds for our benefit
        evaluate = 0
        if not self.curr_board : return evaluate

        for row in range(ROWS):
            for col in range(COlS):
                if self.curr_board.squares[row][col].has_figure():
                    fig = self.curr_board.squares[row][col].figure
                    if fig.color == self.color:
                        evaluate += fig.value
                    else:
                        evaluate -= fig.value

        return evaluate

    def all_posible_moves(
        self, color: Colors
    ) -> list[Move]:  # all posible move for color
        moves = []
        for row in range(ROWS):
            for col in range(COlS):
                if self.curr_board.squares[row][col].has_figure():
                    fig = self.curr_board.squares[row][col].figure
                    if fig.color == color:
                        self.curr_board.find_valid_moves_for_figure(fig, row, col)
                        self.curr_board.remove_invalid_moves(fig)
                        moves.extend(fig.moves)
        return moves

    def get_opponent_color(self) -> Colors:
        return Colors.WHITE if self.color == Colors.BLACK else Colors.BLACK

    def minimax(
        self, depth: int, alpha: float, beta: float, is_ai_turn: bool
    ) -> tuple[Move | None, float]:
        if not self.curr_board: return None, self.evaluate_board()

        board_hash = self.hasher.hash_board(self.curr_board) # int
        
        if (
            board_hash in self.transposition_table
            and self.transposition_table[board_hash]["depth"] >= depth
        ):
            return (
                self.transposition_table[board_hash]["best_move"],
                self.transposition_table[board_hash]["score"],
            )

        if depth == 0:
            return None, self.evaluate_board()

        best_move = None
        if is_ai_turn:
            max_eval = -math.inf
            for move in self.all_posible_moves(self.color):
                fig = copy.deepcopy(
                    self.curr_board.squares[move.original.row][move.original.col].figure
                )

                if fig is None:
                    continue

                self.curr_board.set_new_pos(fig, move)
                _, evaluate = self.minimax(depth - 1, alpha, beta, False)

                if evaluate > max_eval:
                    max_eval = evaluate
                    best_move = move

                alpha = max(alpha, evaluate)
                if beta <= alpha:
                    break

            self.transposition_table[board_hash] = {
                "score": max_eval,
                "best_move": best_move,
                "depth": depth,
            }
            return best_move, max_eval

        else:
            min_eval = math.inf
            for move in self.all_posible_moves(self.get_opponent_color()):
                fig = copy.deepcopy(
                    self.curr_board.squares[move.original.row][move.original.col].figure
                )

                if fig is None:
                    continue

                self.curr_board.set_new_pos(fig, move)
                _, evaluate = self.minimax(depth - 1, alpha, beta, True)

                if evaluate < min_eval:
                    min_eval = evaluate
                    best_move = move

                beta = min(beta, evaluate)
                if beta <= alpha:
                    break

            self.transposition_table[board_hash] = {
                "score": min_eval,
                "best_move": best_move,
                "depth": depth,
            }
            return best_move, min_eval

    def get_best_move(
        self, curr_board: Board
    ) -> Move | None:  # check if is none to return random posible move
        self.curr_board = copy.deepcopy(
            curr_board
        )  # copy the curren board so we can make scenarios of posible best moves
        best_move, _ = self.minimax(self.depth, -math.inf, math.inf, True)
        return best_move
