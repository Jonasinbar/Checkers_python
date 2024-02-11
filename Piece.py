from Player import Player


class Piece:
    def __init__(self, owner: Player, x, y, flagged=False):
        self.owner = owner
        self.y = y
        self.x = x
        self.is_king = False
        self.flagged = flagged
