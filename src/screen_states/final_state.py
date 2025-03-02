import pygame, os
from src.screen_states.state import *
from src.ui_elements import Button


class FinalState(State):

    def __init__(
        self, screen: pygame.Surface, background_color: tuple[int, int, int]
    ) -> None:
        super().__init__(screen, background_color)

        self.button_to_menu = Button(
            335,
            220,
            120,
            40,
            "Back to menu",
            pygame.font.SysFont("Arial", 20),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.button_rank_list = Button(
            349,
            285,
            90,
            40,
            "Rank list",
            pygame.font.SysFont("Arial", 20),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )

        self.font = pygame.font.SysFont("Arial Bold", 30)
        self.image_paths = [
            os.path.join("images", "game_over.png"),
            os.path.join("images", "menu.png"),
        ]

    def _load_images(self) -> None:
        image = pygame.image.load(self.image_paths[1])
        image = pygame.transform.scale(image, (850, 350))
        image_rect = image.get_rect(center=(405, 500))
        self.screen.blit(image, image_rect)
        image = pygame.image.load(self.image_paths[0])
        image = pygame.transform.scale(image, (325, 325))
        image_rect = image.get_rect(center=(395, 100))
        self.screen.blit(image, image_rect)

    def draw_elements(self) -> None:
        self.button_to_menu.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (335, 220, 120, 40), 3)
        self.button_rank_list.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (349, 285, 90, 40), 3)
        self._load_images()

    def handle_events(self, event: pygame.event.Event) -> None:
        self.button_to_menu.handle_event(event)
        self.button_rank_list.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_to_menu.is_clicked(event.pos):
                State.current_state = ScreenState.MENU
            if self.button_rank_list.is_clicked(event.pos) and State.is_load_ranklist:
                State.current_state = ScreenState.ranklist
