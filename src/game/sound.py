import os

import pygame


class Sound:

    def __init__(self, path: list[str]) -> None:
        self.path = os.path.join(*path)
        self.sound = pygame.mixer.Sound(self.path)

    def play(self) -> None:
        pygame.mixer.Sound.play(self.sound)
