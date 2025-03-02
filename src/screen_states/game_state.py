import random
from collections import Counter
from dataclasses import dataclass

import pygame
from src.game.consts import *
from src.game.figure import *
from src.game.board import Board
from src.game.dragger import Dragger
from src.game.figure import Colors
from src.game.sound import Sound
from src.game.move import Move
from src.game.square import Square
from src.ui_elements import Button
from src.ai.ai import *
from src.ranklist import User

from src.screen_states.state import *


@dataclass
class Player:
    user: User
    color: Colors


class GameState(State):
    def __init__(
        self, screen: pygame.Surface, background_color: tuple[int, int, int]
    ) -> None:
        super().__init__(screen, background_color)

        self.lost_figures_white = []  # it will contain the types of figures
        self.lost_figures_black = []
        self.white_player = None
        self.black_player = None
        self.is_game_over = False  # to check if the game is over
        self.is_make_moved = False  # so the ai to wait for our move
        self.loser_color = None  # when game is over to know the outcome for ranklist
        self.counter = 50  # is used for remi if a player is not captured any figure for 50 moves or is not moved a pawn for 50 moves

        self.move_sound = Sound(["sounds", "move.wav"])
        self.capture_sound = Sound(["sounds", "capture.wav"])
        self.font = pygame.font.SysFont("Arial Bold", 17)
        self.next_turn = Colors.WHITE
        self.board = Board()
        self.dragger = Dragger()
        self.ai = AI(AIType.EASY, Colors.BLACK)

        self.button_to_surrender = Button(
            640,
            530,
            110,
            40,
            "To surrender",
            pygame.font.SysFont("Arial", 20),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )

    def _draw_board_numeration(self, row: int, col: int) -> None:
        if col == 0:
            color = SQUARE_COLOR if row % 2 == 0 else BACKGROUND_COLOR
            label = self.font.render(str(ROWS - row), 1, color)
            label_pos = (5, 5 + row * SQUARE_SIZE)

            self.screen.blit(label, label_pos)

    def _draw_column_labels(self, row: int, col: int) -> None:
        if row == 7:
            color = SQUARE_COLOR if (row + col) % 2 == 0 else BACKGROUND_COLOR
            label = self.font.render(self.board.get_alpha_col(col), 1, color)
            label_pos = (col * SQUARE_SIZE + SQUARE_SIZE - 10, GAME_HEIGHT - 10)

            self.screen.blit(label, label_pos)

    def _draw_bg(self) -> None:
        for row in range(ROWS):
            for col in range(COlS):
                color = SQUARE_COLOR if (row + col) % 2 else BACKGROUND_COLOR
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                )

                self._draw_board_numeration(row, col)
                self._draw_column_labels(row, col)

        pygame.draw.rect(self.screen, SQUARE_COLOR, (600, 0, 200, 600), 6)

    def _draw_figures(self) -> None:
        for row, col in [
            (r, c)
            for r in range(ROWS)
            for c in range(COlS)
            if self.board.squares[r][c].has_figure()
        ]:
            figure = self.board.squares[row][col].figure

            if figure is not self.dragger.figure:
                figure.image_with_size(
                    self.screen,
                    0,
                    (
                        col * SQUARE_SIZE + SQUARE_SIZE // 2,
                        row * SQUARE_SIZE + SQUARE_SIZE // 2,
                    ),
                )

    def _draw_moves(self) -> None:
        if self.dragger.is_dragging:
            figure = self.dragger.figure

            for move in figure.moves:
                color = (
                    VALID_MOVES_COLOR_DARKER
                    if (move.final.row + move.final.col) % 2
                    else VALID_MOVES_COLOR_LIGHTER
                )
                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        move.final.col * SQUARE_SIZE,
                        move.final.row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE,
                    ),
                )

    def _draw_last_move(self) -> None:
        if self.board.last_move:
            original = self.board.last_move.original
            final = self.board.last_move.final

            for pos in [original, final]:
                if (pos.row + pos.col) % 2 == 1:
                    rect = (
                        pos.col * SQUARE_SIZE,
                        pos.row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE,
                    )
                    pygame.draw.rect(self.screen, LAST_MOVE_COLOR_DARKER, rect)
                else:
                    rect = (
                        pos.col * SQUARE_SIZE,
                        pos.row * SQUARE_SIZE,
                        SQUARE_SIZE,
                        SQUARE_SIZE,
                    )
                    pygame.draw.rect(self.screen, LAST_MOVE_COLOR_LIGHTER, rect)

    def _format_lost_figures(self, counter: Counter) -> str:
        items = [
            f"{figure_type.name}: {count}" for figure_type, count in counter.items()
        ]
        lines = [" | ".join(items[i : i + 2]) for i in range(0, len(items), 2)]
        return "\n".join(lines)

    def _draw_lost_figures(self):
        white = Counter(self.lost_figures_white)
        black = Counter(self.lost_figures_black)
        white_counts = self._format_lost_figures(white)
        black_counts = self._format_lost_figures(black)

        font_players = pygame.font.SysFont("Arial Bold", 25)
        font_figures = pygame.font.SysFont("Arial", 16)

        text_surface = font_players.render(f"Lost figures:", True, (111, 78, 55))
        text_rect = text_surface.get_rect(center=(700, 25))
        self.screen.blit(text_surface, text_rect)

        # Lost figures for black player
        if self.black_player:

            text_surface = font_players.render(
                f"{self.black_player.user.username}", True, (0, 0, 0)
            )
        else:
            text_surface = font_players.render(f"{self.ai.type=}", True, (0, 0, 0))

        text_rect = text_surface.get_rect(center=(700, 50))
        self.screen.blit(text_surface, text_rect)

        y_offset = 70
        for line in black_counts.split("\n"):
            text_surface = font_figures.render(line, True, (111, 78, 55))
            text_rect = text_surface.get_rect(center=(700, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30  # Space between the lines

        # Lost figures for white player
        text_surface = font_players.render(
            f"{self.white_player.user.username}", True, (255, 255, 255)
        )
        text_rect = text_surface.get_rect(center=(700, 310))
        self.screen.blit(text_surface, text_rect)

        y_offset = 330
        for line in white_counts.split("\n"):
            text_surface = font_figures.render(line, True, (111, 78, 55))
            text_rect = text_surface.get_rect(center=(700, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 30  # Space between the lines

    def draw_elements(self) -> None:  # Must set players before the game started
        if not State.users:
            State.users = [User("", "", 1200), User("", "", 1200)]
        self.white_player = Player(State.users[0], Colors.WHITE)
        self.black_player = (
            Player(State.users[1], Colors.BLACK)
            if State.chosen_mode == GameMode.PLAYER_VS_PLAYER
            else Player(User("AI.EASY", "none", 1200), Colors.BLACK)
        )
        self._draw_bg()
        self._draw_last_move()
        self._draw_moves()
        self._draw_figures()
        self._draw_lost_figures()
        self.button_to_surrender.draw(self.screen)
        pygame.draw.rect(
            self.screen, (111, 78, 55), (640, 530, 110, 40), 3
        )  # board of the button

    def _make_and_visualizate_move(self, move: Move) -> None:
        original = move.original
        final = move.final

        captured = self.board.squares[final.row][final.col].has_figure()
        if isinstance(original.figure, Pawn) and (
            original.col == final.col - 1 or original.col == final.col + 1
        ):
            captured = True

        if self.board.squares[move.final.row][move.final.col].has_figure():
            if original.figure.color == Colors.WHITE:
                self.lost_figures_black.append(
                    self.board.squares[move.final.row][move.final.col].figure.type
                )
            else:
                self.lost_figures_white.append(
                    self.board.squares[move.final.row][move.final.col].figure.type
                )

        elif isinstance(original.figure, Pawn) and captured:
            left_col = move.final.col - 1
            right_col = move.final.col + 1
            row = move.final.row
            if original.col == left_col:
                self._add_lost_pawn_by_en_passant(original.figure, row, left_col)
            else:
                self._add_lost_pawn_by_en_passant(original.figure, row, right_col)


        self.board.set_new_pos(original.figure, move)
        self.board.set_en_passant(original.figure)
        self.sound_effect(captured)

        # set the remi counter
        if captured or isinstance(original.figure, Pawn):
            self.counter = 50  # reset the remi counter
        else:
            self.counter -= 1  # not a good move

        self.set_next_turn()
        self.set_game_over(self.next_turn)  # Check if the game is over after the move

        self._draw_bg()
        self._draw_last_move()
        self._draw_figures()

    def _handle_event_mouse_button_down(self, event: pygame.event.Event) -> None:

        if self.button_to_surrender.is_clicked(event.pos):
            self.loser_color = self.next_turn
            self.is_game_over = True
            self._end_game()
        else:
            self.dragger.update_pos(event.pos)
            clicked_row = self.dragger.pos_y // SQUARE_SIZE
            clicked_col = self.dragger.pos_x // SQUARE_SIZE

            if self.board.squares[clicked_row][clicked_col].has_figure():
                self.dragger.save_original_pos(event.pos)
                dragged_figure = self.board.squares[clicked_row][clicked_col].figure

                if (
                    State.chosen_mode == GameMode.PLAYER_VS_AI
                    and dragged_figure.color == self.ai.color
                ):
                    return  # so we can not dragg ai's figures

                if dragged_figure.color == self.next_turn:
                    self.board.find_valid_moves_for_figure(
                        dragged_figure, clicked_row, clicked_col, True
                    )

                    self.board.remove_invalid_moves(
                        dragged_figure
                    )  # cleaning if there is some invalid move
                    self.dragger.save_dragged_figure(dragged_figure)

                    self._draw_bg()
                    self._draw_moves()
                    self._draw_figures()

    def _handle_event_mouse_motion(self, event: pygame.event.Event) -> None:
        if self.dragger.is_dragging:
            self.dragger.update_pos(event.pos)
            self._draw_bg()
            self._draw_last_move()
            self._draw_moves()
            self._draw_figures()
            self.dragger.update_screen(self.screen)

    def _handle_event_mouse_button_up(self, event: pygame.event.Event) -> None:
        if self.dragger.is_dragging:
            self.dragger.update_pos(event.pos)
            dragged_figure = self.dragger.figure

            released_row = (
                self.dragger.pos_y // SQUARE_SIZE
            )  # so we can find in which square we are trying to move the figure
            released_col = self.dragger.pos_x // SQUARE_SIZE

            original = Square(
                self.dragger.original_row, self.dragger.original_col, dragged_figure
            )
            final = Square(released_row, released_col)
            move = Move(original, final)

            if self.board.is_valid_move(original.figure, move):
                self._make_and_visualizate_move(move)

                if State.chosen_mode == GameMode.PLAYER_VS_AI:
                    self.is_make_moved = True

        self.dragger.undragg_figure()

    def gen_ai_move(self) -> None:
        best_move = self.ai.get_best_move(self.board)
        move = (
            best_move
            if best_move
            else random.choice(self.ai.all_posible_moves(self.ai.color))
        )
        self._make_and_visualizate_move(move)
        self.is_make_moved = False

    def handle_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_event_mouse_button_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self._handle_event_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_event_mouse_button_up(event)
            self.set_game_over(self.next_turn)
            if (
                State.chosen_mode == GameMode.PLAYER_VS_AI
                and not self.is_game_over
                and self.is_make_moved
            ):
                self.gen_ai_move()
                self.set_game_over(self.next_turn)

    def _add_lost_pawn_by_en_passant(self, figure: Pawn, row: int, col: int) -> None:
        if Square.in_range(col):
            if figure.color == Colors.WHITE:
                self.lost_figures_black.append(FigureType.PAWN)
            else:
                self.lost_figures_white.append(FigureType.PAWN)

    def set_next_turn(self) -> None:
        self.next_turn = (
            Colors.BLACK if self.next_turn == Colors.WHITE else Colors.WHITE
        )

    def sound_effect(self, captured: bool = False) -> None:
        self.capture_sound.play() if captured else self.move_sound.play()

    def set_game_over(self, curr_turn: Colors) -> None:
        # check if our king is captured
        is_white_loser = any(
            type == FigureType.KING for type in self.lost_figures_white
        )
        is_black_loser = any(
            type == FigureType.KING for type in self.lost_figures_black
        )
        if is_white_loser or is_black_loser:
            self.is_game_over = True
            self.loser_color = Colors.WHITE if is_white_loser else Colors.BLACK

        elif self.board.is_checkmate(curr_turn):
            self.is_game_over = True
            self.loser_color = curr_turn

        elif self.counter <= 0:
            self.is_game_over = True
            self.loser_color = None

        if self.is_game_over:
            self._end_game()

    def _end_game(self) -> None:
        if State.is_load_ranklist:
            if self.loser_color is None:
                State.ranklist.update_elo(
                    self.white_player.user, self.black_player.user, 1 / 2
                )
            elif self.loser_color == Colors.WHITE:
                State.ranklist.update_elo(
                    self.white_player.user, self.black_player.user, 0
                )
            else:
                State.ranklist.update_elo(
                    self.white_player.user, self.black_player.user, 1
                )

            State.current_state = ScreenState.FINAL
        
    def reset(
        self,
    ) -> None:  # reset the game for next playing without closing the pygame window
        self.__init__(self.screen, BACKGROUND_COLOR)
