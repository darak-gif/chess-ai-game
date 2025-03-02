import pygame
from src.ui_elements import Button
from src.screen_states.state import State, ScreenState
from src.ranklist import RankList


class RankListState(State):
    def __init__(
        self, screen: pygame.Surface, background_color: tuple[int, int, int]
    ) -> None:
        super().__init__(screen, background_color)
        self.button_to_menu = Button(
            320,
            545,
            120,
            40,
            "Back to menu",
            pygame.font.SysFont("Arial", 20),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.font = pygame.font.SysFont("Arial Bold", 30)
        self._data = State.ranklist.get_rank_list() if State.is_load_ranklist else []

    def draw_elements(self) -> None:
        title_surface = self.font.render("Ranking List", True, (111, 78, 55))
        title_rect = title_surface.get_rect(center=(380, 30))
        self.screen.blit(title_surface, title_rect)

        header_surface = self.font.render(
            "#        USERNAME                                                  SCORE",
            True,
            (111, 78, 55),
        )
        header_rect = header_surface.get_rect(center=(300, 80))
        self.screen.blit(header_surface, header_rect)

        row_height = 40
        start_y = 80  # Starting point for the first row

        colors = [(248, 253, 213), (222, 217, 186)]  # alternate two colors
        for index, (username, data) in enumerate(self._data.items(), start=1):
            score = data["score"]
            bg_color = colors[index % 2]

            pygame.draw.rect(
                self.screen,
                bg_color,
                (0, start_y + index * row_height, 800, row_height),
            )
            spacing = " " * (70 - len(username))
            text = f"{index:<4}   {username}{spacing}{score:<5}"
            text_surface = self.font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(
                midleft=(30, start_y + index * row_height + row_height // 2)
            )
            self.screen.blit(text_surface, text_rect)

        self.button_to_menu.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (320, 545, 120, 40), 3)

    def handle_events(self, event: pygame.event.Event) -> None:
        self.button_to_menu.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and self.button_to_menu.is_clicked:
            State.current_state = ScreenState.MENU
