import pygame, os
from src.ui_elements import Button
from src.screen_states.state import State, ScreenState, GameMode


class MenuState(State):
    def __init__(
        self, screen: pygame.Surface, background_color: tuple[int, int, int]
    ) -> None:
        super().__init__(screen, background_color)
        self.button_pvp = Button(
            280,
            250,
            250,
            50,
            "Player VS Player",
            pygame.font.SysFont("Arial Bold", 40),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.button_ai = Button(
            280,
            350,
            250,
            50,
            "Player VS AI",
            pygame.font.SysFont("Arial Bold", 40),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.button_rank_list = Button(
            620,
            520,
            90,
            40,
            "Rank list",
            pygame.font.SysFont("Arial", 20),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.font = pygame.font.SysFont("Arial Bold", 30)
        self.image_path = os.path.join("images", "menu2.png")

    def _load_image(self) -> None:
        image = pygame.image.load(self.image_path)
        image = pygame.transform.scale(image, (300, 270))
        image_rect = image.get_rect(topleft=(40, 350))
        self.screen.blit(image, image_rect)

    def _load_text(self) -> None:
        text_surface = self.font.render(
            "WELCOME TO OUR CHESS WORLD!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 120))
        self.screen.blit(text_surface, text_rect)
        text_surface = self.font.render(
            "Choose the game mood you want to play!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 170))
        self.screen.blit(text_surface, text_rect)

    def draw_elements(self) -> None:
        self._load_text()
        self.button_pvp.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (280, 250, 250, 50), 5)
        self.button_ai.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (280, 350, 250, 50), 5)
        self.button_rank_list.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (620, 520, 90, 40), 3)
        self._load_image()

    def handle_events(self, event: pygame.event.Event) -> None:
        self.button_pvp.handle_event(event)
        self.button_ai.handle_event(event)
        self.button_rank_list.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_pvp.is_clicked(event.pos):
                State.chosen_mode = GameMode.PLAYER_VS_PLAYER
                State.current_state = ScreenState.REGISTER

            if self.button_ai.is_clicked(event.pos):
                State.chosen_mode = GameMode.PLAYER_VS_AI
                State.current_state = ScreenState.REGISTER

            if self.button_rank_list.is_clicked(event.pos) and State.is_load_ranklist:
                State.current_state = ScreenState.ranklist

    def restart(self) -> None:
        self.__init__(self.screen, self.background_color)
