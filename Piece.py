from Player import Player


class Piece:
    def __init__(self, owner: Player, x, y, is_flagged=False):
        self.owner = owner
        self.y = y
        self.x = x
        self.is_king = False
        self.is_flagged = is_flagged
