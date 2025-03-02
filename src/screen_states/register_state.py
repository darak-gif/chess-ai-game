import pygame
from pygame.locals import *
from src.ui_elements import Button, Inbox
from src.screen_states.state import State, ScreenState, GameMode
from src.ranklist import  User


class RegisterState(State):
    def __init__(self, screen: pygame.Surface, background_color: tuple[int, int, int]):
        super().__init__(screen, background_color)
        self.inbox_username = Inbox(
            250,
            250,
            300,
            50,
            pygame.font.SysFont("Arial", 12),
            "Enter your username...",
            False,
            (0, 0, 0),
            (248, 253, 213),
            (111, 78, 55),
        )
        self.inbox_password = Inbox(
            250,
            310,
            300,
            50,
            pygame.font.SysFont("Arial", 12),
            "Enter your password...",
            True,
            (0, 0, 0),
            (248, 253, 213),
            (111, 78, 55),
        )
        self.button_login = Button(
            275,
            400,
            250,
            50,
            "Login  or  Registration",
            pygame.font.SysFont("Arial Bold", 24),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.button_to_menu = Button(
            330,
            545,
            120,
            40,
            "Back to menu",
            pygame.font.SysFont("Arial", 20),
            colors={"normal": "#d8d5b9", "hover": "#eee8aa", "pressed": "#333333"},
        )
        self.font = pygame.font.SysFont("Arial Bold", 30)
        self.user = User("", "", 1200)  # default user
        self._show_registration_message = False
        self._show_used_nickname = False
        self.count_reg = 0

    def draw_elements(self) -> None:
        text_surface = self.font.render(
            "Please login in your profile!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 150))
        self.screen.blit(text_surface, text_rect)
        self.inbox_username.draw(self.screen)
        self.inbox_password.draw(self.screen)
        self.button_login.draw(self.screen)
        pygame.draw.rect(self.screen, (111, 78, 55), (275, 400, 250, 50), 5)
        if self._show_used_nickname:
            self.already_used_nickname()
        if self._show_registration_message:
            self.make_registration()
            self.button_to_menu.draw(self.screen)
            pygame.draw.rect(self.screen, (111, 78, 55), (330, 545, 120, 40), 3)
        if not State.is_load_ranklist:
            self.can_not_reach_data()

    def already_used_nickname(self) -> None:
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Wrong login password or this nickname is already in use and you CANNOT register in with it!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 200))
        self.screen.blit(text_surface, text_rect)
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Please enter the right password or a new nickname!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 225))
        self.screen.blit(text_surface, text_rect)

    def make_registration(self) -> None:
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "There is no account with this username and password.", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 200))
        self.screen.blit(text_surface, text_rect)
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Do you want to create an account with this data?", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 225))
        self.screen.blit(text_surface, text_rect)
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Press the button again for Yes!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 480))
        self.screen.blit(text_surface, text_rect)

    def can_not_reach_data(self) -> None:
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Sorry, we have a problem with our database right now.", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 200))
        self.screen.blit(text_surface, text_rect)
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Do you want to play without saving your new score?", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(400, 225))
        self.screen.blit(text_surface, text_rect)
        text_surface = pygame.font.SysFont("Arial", 20).render(
            "Press the button for Yes!", True, (111, 78, 55)
        )
        text_rect = text_surface.get_rect(center=(405, 480))
        self.screen.blit(text_surface, text_rect)

    def handle_events(self, event: pygame.event.Event) -> None:
        self.inbox_username.handle_event(event)
        self.inbox_password.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if self.inbox_username.active:
                if event.key == pygame.K_RETURN:
                    self.user.username = self.inbox_username.last_input

            if self.inbox_password.active:
                if event.key == pygame.K_RETURN:
                    self.user.password = self.inbox_password.last_input
                    if State.is_load_ranklist:
                        if not State.ranklist.is_already_has_account(self.user):
                            if State.ranklist.already_used_nickname(self.user):
                                self._show_used_nickname = True
                            else :
                                self._show_used_nickname = False
                                self._show_registration_message = True
                        else:
                            self._show_used_nickname = False
                    # if (
                    #     State.is_load_ranklist
                    #     and not State.ranklist.is_already_has_account(self.user)
                    # ):
                    #     self._show_registration_message = True

        self.button_login.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and self.button_login.is_clicked(
            event.pos
        ):

            if not State.is_load_ranklist:
                State.current_state = ScreenState.GAME
            else:

                if not self.user.username or not self.user.password:
                    return  # so user must enter username and password for registration

                if self._show_registration_message:  # new user
                    State.users.append(self.user)  # here add Users fo the game_state
                    self._show_registration_message = False

                    State.ranklist.add_new_user(self.user)
                else:  # already have an account so we check the score
                    self.user.score = State.ranklist.get_user_score(self.user.username)
                    State.users.append(self.user)  # here add Users for the game_state
                if State.chosen_mode == GameMode.PLAYER_VS_AI or (
                    State.chosen_mode == GameMode.PLAYER_VS_PLAYER
                    and self.count_reg == 1
                ):
                    State.current_state = ScreenState.GAME
                else:
                    State.current_state = ScreenState.REGISTER
                    self.count_reg += 1

                    self.user = User("", "", 1200)

        elif event.type == pygame.MOUSEBUTTONDOWN and self.button_to_menu.is_clicked(
            event.pos
        ):
            self._show_registration_message = False
            State.current_state = ScreenState.MENU
