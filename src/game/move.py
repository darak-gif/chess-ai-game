from src.game.square import Square


class Move:

    def __init__(self, original: Square, final: Square) -> None:
        self.original = original
        self.final = final

    def __eq__(self, other) -> bool:
        return self.original == other.original and self.final == other.final
