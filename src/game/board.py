from src.game.consts import *
from src.game.figure import *
from src.game.square import Square
from src.game.move import Move

import copy


class Board:

    def __init__(self) -> None:
        self.squares = [
            [
                Square(0, col),
                Square(1, col),
                Square(2, col),
                Square(3, col),
                Square(4, col),
                Square(5, col),
                Square(6, col),
                Square(7, col),
            ]
            for col in range(COlS)
        ]
        self.squares_alphabet = {
            0: "A",
            1: "B",
            2: "C",
            3: "D",
            4: "E",
            5: "F",
            6: "G",
            7: "H",
        }
        self._create()
        self._add_figures(Colors.WHITE)
        self._add_figures(Colors.BLACK)

        self.last_move = None

    def _create(self) -> None:
        for row in range(ROWS):
            for col in range(COlS):
                self.squares[row][col] = Square(row, col)

    def _add_figures(self, color: Colors) -> None:
        row_pawns, row_others = (6, 7) if color == Colors.WHITE else (1, 0)

        for col in range(COlS):
            self.squares[row_pawns][col] = Square(row_pawns, col, Pawn(color))

        self.squares[row_others][1] = Square(row_others, 1, Knight(color))
        self.squares[row_others][6] = Square(row_others, 6, Knight(color))

        self.squares[row_others][2] = Square(row_others, 2, Bishop(color))
        self.squares[row_others][5] = Square(row_others, 5, Bishop(color))

        self.squares[row_others][0] = Square(row_others, 0, Rook(color))
        self.squares[row_others][7] = Square(row_others, 7, Rook(color))

        self.squares[row_others][3] = Square(row_others, 3, Queen(color))

        self.squares[row_others][4] = Square(row_others, 4, King(color))

    def _validate_moves_of_Pawn(
        self, figure: Pawn, row: int, col: int
    ) -> list[tuple[int, int]]:
        valid_moves = []
        step = 1 if figure.moved else 2
        start = row + figure.dir
        end = row + (figure.dir * (step + 1))

        # straight moves
        for move_row in range(start, end, figure.dir):
            if Square.in_range(move_row, col):
                if self.squares[move_row][col].is_empty():
                    valid_moves.append((move_row, col))
                else:
                    break
            else:
                break

        # diagonal moves
        for posible_move in [(row + figure.dir, col + 1), (row + figure.dir, col - 1)]:
            posible_move_row, posible_move_col = posible_move
            if Square.in_range(posible_move_row, posible_move_col) and self.squares[
                posible_move_row
            ][posible_move_col].has_opponent_figure(figure.color):
                valid_moves.append((posible_move_row, posible_move_col))

        return valid_moves

    def _validate_moves_of_Knight(
        self, figure: Knight, row: int, col: int
    ) -> list[tuple[int, int]]:
        possible_moves = [
            (row - 1, col - 2),
            (row + 1, col - 2),
            (row - 1, col + 2),
            (row + 1, col + 2),
            (row + 2, col - 1),
            (row + 2, col + 1),
            (row - 2, col - 1),
            (row - 2, col + 1),
        ]

        return [
            (r, c)
            for r, c in possible_moves
            if Square.in_range(r, c)
            and (
                self.squares[r][c].is_empty()
                or self.squares[r][c].has_opponent_figure(figure.color)
            )
        ]

    def _remove_blocked_moves(
        self, figure: Figure, list_posible_moves: list[list[tuple[int, int]]]
    ) -> list[tuple[int, int]]:
        valid_moves = []
        for posible_moves in list_posible_moves:
            for posible_move in posible_moves:
                posible_move_row, posible_move_col = posible_move
                if Square.in_range(posible_move_row, posible_move_col):
                    if self.squares[posible_move_row][posible_move_col].is_empty():
                        valid_moves.append((posible_move_row, posible_move_col))
                    elif self.squares[posible_move_row][
                        posible_move_col
                    ].has_opponent_figure(figure.color):
                        valid_moves.append((posible_move_row, posible_move_col))
                        break  # we found figure
                    else:
                        break
                else:
                    break
        return valid_moves

    def _validate_moves_of_Bishop(
        self, figure: Figure, row: int, col: int
    ) -> list[tuple[int, int]]:
        directions = [(-1, 1), (-1, -1), (1, 1), (1, -1)]
        possible_moves = [
            [(row + i * dr, col + i * dc) for i in range(1, 8)] for dr, dc in directions
        ]

        return self._remove_blocked_moves(figure, possible_moves)

    def _validate_moves_of_Rook(
        self, figure: Figure, row: int, col: int
    ) -> list[tuple[int, int]]:
        directions = [(0, 1), (0, -1), (-1, 0), (1, 0)]
        possible_moves = [
            [(row + i * dr, col + i * dc) for i in range(1, 8)] for dr, dc in directions
        ]

        return self._remove_blocked_moves(figure, possible_moves)

    def _validate_moves_of_Queen(
        self, figure: Queen, row: int, col: int
    ) -> list[tuple[int, int]]:
        return self._validate_moves_of_Bishop(
            figure, row, col
        ) + self._validate_moves_of_Rook(figure, row, col)

    def _validate_moves_of_King(
        self, figure: King, row: int, col: int
    ) -> list[tuple[int, int]]:
        possible_moves = [
            (row - 1, col),
            (row + 1, col),
            (row, col + 1),
            (row, col - 1),
            (row - 1, col + 1),
            (row + 1, col + 1),
            (row - 1, col - 1),
            (row + 1, col - 1),
        ]

        return [
            (r, c)
            for r, c in possible_moves
            if Square.in_range(r, c)
            and (
                self.squares[r][c].is_empty()
                or self.squares[r][c].has_opponent_figure(figure.color)
            )
        ]

    def _check_and_add_en_passant_move(
        self, left_or_right: str, figure: Pawn, row: int, col: int, recursion: bool
    ) -> None:
        r = 3 if figure.color == Colors.WHITE else 4
        fr = 2 if figure.color == Colors.WHITE else 5
        c = col - 1 if left_or_right == "left" else col + 1

        if Square.in_range(c) and row == r:
            if self.squares[row][c].has_opponent_figure(figure.color):
                fig = self.squares[row][c].figure
                if isinstance(fig, Pawn) and fig.en_passant:
                    original = Square(row, col)
                    final = Square(fr, c)
                    move = Move(original, final)

                    if recursion:
                        # check for potencial check before add to figure.moves
                        if not self.in_check(figure, move):
                            figure.add_move(move)
                    else:
                        figure.add_move(move)

    def _check_and_add_castling_move(
        self, left_or_right: str, figure: King, row: int, col: int, recursion: bool
    ) -> None:
        castling_data = {"left": (0, [1, 2, 3], 3, 2), "right": (7, [5, 6], 5, 6)}
        rook_col, check_cols, rook_final_col, king_final_col = castling_data[
            left_or_right
        ]

        if (
            isinstance((rook := self.squares[row][rook_col].figure), Rook)
            and not rook.moved
        ):
            if all(self.squares[row][c].is_empty() for c in check_cols):
                if left_or_right == "left":
                    figure.left_rook = rook
                else:
                    figure.right_rook = rook

                moveK = Move(Square(row, col), Square(row, king_final_col))
                moveR = Move(Square(row, rook_col), Square(row, rook_final_col))

                if not recursion or (
                    not self.in_check(figure, moveK)
                    and not self.in_check(figure, moveR)
                ):
                    figure.add_move(moveK)
                    rook.add_move(moveR)

    def find_valid_moves_for_figure(
        self, figure: Figure, row: int, col: int, recursion: bool = True
    ) -> None:

        if isinstance(figure, Pawn):
            valid_moves = self._validate_moves_of_Pawn(figure, row, col)
        elif isinstance(figure, Knight):
            valid_moves = self._validate_moves_of_Knight(figure, row, col)
        elif isinstance(figure, Bishop):
            valid_moves = self._validate_moves_of_Bishop(figure, row, col)
        elif isinstance(figure, Rook):
            valid_moves = self._validate_moves_of_Rook(figure, row, col)
        elif isinstance(figure, Queen):
            valid_moves = self._validate_moves_of_Queen(figure, row, col)
        elif isinstance(figure, King):
            valid_moves = self._validate_moves_of_King(figure, row, col)

        for valid_move in valid_moves:
            valid_move_row, valid_move_col = valid_move
            original = Square(row, col, figure)
            final_figure = self.squares[valid_move_row][
                valid_move_col
            ].figure  # this will be used for checking if the final square contains the opponent's king
            final = Square(valid_move_row, valid_move_col, final_figure)
            move = Move(original, final)

            if recursion:
                # check for potencial check before add to figure.moves
                if not self.in_check(figure, move):
                    figure.add_move(move)
            else:
                figure.add_move(move)

        if isinstance(figure, Pawn):
            self._check_and_add_en_passant_move("left", figure, row, col, recursion)
            self._check_and_add_en_passant_move("right", figure, row, col, recursion)

        if isinstance(figure, King) and not figure.moved:
            self._check_and_add_castling_move("left", figure, row, col, recursion)
            self._check_and_add_castling_move("right", figure, row, col, recursion)

    def set_new_pos(self, figure: Figure, move: Move) -> None:
        original = move.original
        final = move.final

        # before we set the figure to None
        en_passant_empty = self.squares[final.row][final.col].is_empty()

        self.squares[original.row][original.col].figure = None
        self.squares[final.row][final.col].figure = figure

        if isinstance(figure, Pawn):
            # pawn en passant
            diff = final.col - original.col
            if diff != 0 and en_passant_empty:  # to show the capturing
                self.squares[original.row][original.col + diff].figure = None
                self.squares[final.row][final.col].figure = figure
            else:
                # pawn promotion
                self.check_promotion(figure, final)

        # king castling
        if isinstance(figure, King) and self.check_castling(original, final):
            is_left_or_right = final.col - original.col
            rook = figure.left_rook if (is_left_or_right < 0) else figure.right_rook
            if isinstance(rook, Rook) and rook.moves:
                self.set_new_pos(
                    rook, rook.moves[-1]
                )  # the king is moved already so now we should move the rook

        figure.moved = True
        figure.clear_moves()
        self.last_move = move

    def is_valid_move(self, figure: Figure, move: Move) -> bool:
        return move in figure.moves

    def check_promotion(self, figure: Figure, final: Square) -> None:
        if final.row == 0 or final.row == 7:
            self.squares[final.row][final.col].figure = Queen(figure.color)

    def check_castling(self, original: Square, final: Square) -> bool:
        return (
            abs(original.col - final.col) == 2
        )  # only way for the king to move with more than 1 step

    def set_en_passant(self, figure: Figure) -> None:
        # if not isinstance(figure,Pawn): return
        for row in range(ROWS):
            for col in range(COlS):
                if isinstance(self.squares[row][col].figure, Pawn):
                    self.squares[row][col].figure.en_passant = False

        if isinstance(figure, Pawn):
            figure.en_passant = True

    def in_check(self, figure: Figure, move: Move) -> bool:
        temp_board = copy.deepcopy(
            self
        )  # copy the board so we can move figures to see if they are in check
        temp_figure = copy.deepcopy(
            figure
        )  # so we can move the figure in temporary board
        temp_board.set_new_pos(
            temp_figure, move
        )  # and now we must see if in the final square is a opponent's king

        for row in range(ROWS):
            for col in range(COlS):
                if temp_board.squares[row][col].has_opponent_figure(
                    figure.color
                ):  # looking into all opponent's figures
                    fig = temp_board.squares[row][
                        col
                    ].figure  # the figure that is threatening our king
                    temp_board.find_valid_moves_for_figure(fig, row, col, False)
                    for move in fig.moves:
                        if isinstance(move.final.figure, King):
                            return True  # if this is true we must remove this move from valid moves

        return False

    def is_checkmate(self, color: Colors) -> bool:
        for row in range(ROWS):
            for col in range(COlS):
                # looking into all my figures
                if self.squares[row][col].has_team_figure(color):
                    # the figure that i check for valid_move
                    fig = self.squares[row][col].figure
                    self.find_valid_moves_for_figure(fig, row, col)
                    if fig.moves:
                        return False
        return True

    def remove_invalid_moves(self, figure: Figure) -> None:
        figure.moves = list(
            filter(
                lambda move: self.squares[move.final.row][
                    move.final.col
                ].is_empty()
                or self.squares[move.final.row][
                    move.final.col
                ].has_opponent_figure(figure.color),
                figure.moves,
            )
        )

    def get_alpha_col(self, col: int) -> str:
        return self.squares_alphabet[col]
