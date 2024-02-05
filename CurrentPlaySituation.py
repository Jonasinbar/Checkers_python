class CurrentPlaySituation:
    def __init__(self, board, player1, player2, selected_piece_move_options, selected_piece, pieces_that_can_eat, player_turn, winner,
                 nbr_of_players):
        self.board = board
        self.player1 = player1
        self.player2 = player2
        self.selected_piece_move_options = selected_piece_move_options
        self.selected_piece = selected_piece
        self.pieces_that_can_eat = pieces_that_can_eat
        self.player_turn = player_turn
        self.winner = winner
        self.nbr_of_players = nbr_of_players
