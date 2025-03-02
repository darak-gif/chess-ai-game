import pygame, sys
from src.game.consts import *
from src.game.figure import *
from src.screen_states.state import *
from src.screen_states.menu_state import MenuState
from src.screen_states.register_state import RegisterState
from src.screen_states.ranklist_state import RankListState
from src.screen_states.game_state import GameState
from src.screen_states.final_state import FinalState


class Main:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((APP_WIDTH, APP_HEIGHT))
        pygame.display.set_caption("Chess  game")
        self.menu = MenuState(self.screen, BACKGROUND_COLOR)
        self.register = RegisterState(self.screen, BACKGROUND_COLOR)
        self.game = GameState(self.screen, BACKGROUND_COLOR)
        self.ranklist = RankListState(self.screen, BACKGROUND_COLOR)
        self.final = FinalState(self.screen, BACKGROUND_COLOR)

    def mainloop(self) -> None:

        screen = self.screen

        while True:

            screen.fill(BACKGROUND_COLOR)  # to clean the screen

            if State.current_state == ScreenState.MENU:
                self.menu.draw_elements()

            elif State.current_state == ScreenState.REGISTER:
                self.register.draw_elements()

            elif State.current_state == ScreenState.GAME:
                self.game.draw_elements()
                if self.game.dragger.is_dragging:
                    self.game.dragger.update_screen(screen)

            elif State.current_state == ScreenState.ranklist:
                self.ranklist.draw_elements()

            elif State.current_state == ScreenState.FINAL:
                self.game.reset()
                self.final.draw_elements()

            for event in pygame.event.get():

                if (
                    event.type == pygame.QUIT
                    and State.current_state != ScreenState.GAME
                ):
                    if State.is_load_ranklist:
                        State.ranklist.save_ranklist()
                    pygame.quit()
                    sys.exit()

                if State.current_state == ScreenState.MENU:
                    self.menu.handle_events(event)

                elif State.current_state == ScreenState.REGISTER:
                    self.register.handle_events(event)

                elif State.current_state == ScreenState.GAME:
                    self.game.handle_events(event)

                elif State.current_state == ScreenState.ranklist:
                    self.ranklist.handle_events(event)

                elif State.current_state == ScreenState.FINAL:
                    self.final.handle_events(event)

            pygame.display.update()


main = Main()
main.mainloop()
