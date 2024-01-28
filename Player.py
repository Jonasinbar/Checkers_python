class Player:
    def __init__(self, name, color, direction, captured_pieces: int):
        self.name = name
        self.color = color
        self.direction = direction
        self.captured_pieces = captured_pieces

    def __eq__(self, other):
        return getattr(self, "color", "_") == getattr(other, "color", "")
