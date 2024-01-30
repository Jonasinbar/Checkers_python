class CurrentPlaySituation:
    def __init__(self, grid, player1, player2, possible_moves, selected_piece, pieces_that_can_eat, player_turn, winner,
                 nbr_of_players):
        self.grid = grid
        self.player1 = player1
        self.player2 = player2
        self.possible_moves = possible_moves
        self.selected_piece = selected_piece
        self.pieces_that_can_eat = pieces_that_can_eat
        self.player_turn = player_turn
        self.winner = winner
        self.nbr_of_players = nbr_of_players
