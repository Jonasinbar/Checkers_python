from Piece import Piece
from Player import Player


class GameState:
    def __init__(self, player_turn: Player, selected_piece: Piece, selected_piece_move_options, pieces_that_can_eat, piece_that_have_to_eat_again):
        self.player_turn = player_turn
        self.selected_piece = selected_piece
        self.selected_piece_move_options = selected_piece_move_options
        self.pieces_that_can_eat = pieces_that_can_eat
        self.piece_that_have_to_eat_again = piece_that_have_to_eat_again
        self.winner = None
