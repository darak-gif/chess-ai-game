import pygame
from pygame.locals import *
from abc import ABC, abstractmethod


class UIElement(ABC):
    def __init__(self, x: int, y: int, width: int, heigth: int) -> None:
        self.rect = pygame.Rect(x, y, width, heigth)

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        pass


class Button(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        button_text: str,
        font: pygame.font.Font,
        colors: dict,
        text_color: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        super().__init__(x, y, width, height)
        self.button_text = button_text
        self.colors = colors
        self.text_color = text_color
        self.font = font
        self.current_color = self.colors["normal"]
        self.is_pressed = False

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.current_color, self.rect)

        text_surf = self.font.render(self.button_text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)

        screen.blit(text_surf, text_rect)  # Show the text at the screen

    def handle_event(self, event: pygame.event.Event) -> None:

        if event.type == pygame.MOUSEMOTION:

            if self.rect.collidepoint(event.pos):
                self.current_color = self.colors["hover"]
            else:
                self.current_color = self.colors["normal"]

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if self.rect.collidepoint(event.pos):
                self.current_color = self.colors["pressed"]
                self.is_pressed = True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed == True:
                self.current_color = (
                    self.colors["hover"]
                    if self.rect.collidepoint(event.pos)
                    else self.colors["normal"]
                )
                self.is_pressed = False

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(mouse_pos)


class Inbox(UIElement):
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        font: pygame.font.Font,
        placeholder: str = "",
        hidden_input: bool = True,
        text_color: tuple[int, int, int] = (0, 0, 0),
        box_color: tuple[int, int, int] = (255, 255, 255),
        border_color: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        super().__init__(x, y, width, height)
        self.font = font
        self.placeholder = placeholder
        self.hidden_input = hidden_input
        self.input = ""
        self.last_input = ""
        self.text_color = text_color
        self.box_color = box_color
        self.border_color = border_color
        self.active = False
        self.placeholder_active = True

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.box_color, self.rect)
        pygame.draw.rect(
            screen, self.border_color, self.rect, 2
        )  # border aroud the box with width 2

        if self.input or not self.placeholder_active:
            display_text = (
                "*" * len(self.input) if self.hidden_input else self.input
            )  # this way for password will see *
            text_surf = self.font.render(display_text, True, self.text_color)
        else:
            text_surf = self.font.render(self.placeholder, True, (150, 150, 150))

        text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
        screen.blit(text_surf, text_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.handle_click(event)

        if event.type == pygame.KEYDOWN: 
            if self.active: 
                if event.key == pygame.K_RETURN: 
                    self.last_input = self.input
                    self.input = ""
                    self.placeholder_active = True
                elif event.key == pygame.K_BACKSPACE:
                    self.input = self.input[:-1]
                else:
                    self.input += event.unicode

    def handle_click(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(
                event.pos
            )  # to check if the inputbox is clicked for typing

    def update(self) -> None:
        self.placeholder_active = not bool(self.input)

    def get_text(self) -> str:
        return self.input
