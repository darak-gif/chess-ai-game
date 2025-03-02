from enum import Enum
from abc import ABC, abstractmethod
import pygame

from src.ranklist import RankList


class ScreenState(Enum):
    MENU = 1
    REGISTER = 2
    GAME = 3
    ranklist = 4
    FINAL = 5


class GameMode(Enum):
    PLAYER_VS_PLAYER = 1
    PLAYER_VS_AI = 2


class State(ABC):
    current_state = ScreenState.MENU  # this is shared data
    chosen_mode = GameMode.PLAYER_VS_PLAYER
    is_load_ranklist = False
    users = []  # set users in register_state
    try:
        ranklist = RankList(["ranklist.txt"], 32)
        is_load_ranklist = True
    except (OSError, RuntimeError, ValueError) as e:
        is_load_ranklist = False

    def __init__(
        self, screen: pygame.Surface, background_color: tuple[int, int, int]
    ) -> None:
        self.screen = screen
        self.background_color = background_color

    @abstractmethod
    def draw_elements(self) -> None:
        pass

    @abstractmethod
    def handle_events(self, event: pygame.event.Event) -> None:
        pass
