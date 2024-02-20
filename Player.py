import random
from copy import deepcopy
from CheckersMove import CheckersMove


class Player:
    def __init__(self, name, color, direction, captured_pieces: int):
        self.name = name
        self.color = color
        self.direction = direction
        self.captured_pieces = captured_pieces

    def __eq__(self, other):
        return getattr(self, "color", "_") == getattr(other, "color", "")


def is_move_eating_my_piece(eat_move, grid):
    eaten_piece = None
    piece = grid[eat_move.start_x][eat_move.start_y]
    if not piece.is_king and (abs(eat_move.start_x - eat_move.end_x) > 1 or abs(eat_move.start_y - eat_move.end_y) > 1):
        eaten_piece_x = int((eat_move.start_x + eat_move.end_x) / 2)
        eaten_piece_y = int((eat_move.start_y + eat_move.end_y) / 2)
        eaten_piece = grid[eaten_piece_x][eaten_piece_y]
    elif piece.is_king:
        is_eat_move, eaten_piece_coor = is_eat_move_from_king(eat_move, grid)
        eaten_piece = grid[eaten_piece_coor[0]][eaten_piece_coor[1]]

    if eaten_piece and eaten_piece.is_flagged:
        return True


def is_moved_piece_in_danger(new_grid_after_move, move):
    moved_piece = new_grid_after_move[move.end_x][move.end_y]
    for row in new_grid_after_move:
        for piece in row:
            if piece:
                if piece.owner != moved_piece.owner:
                    from Board import Board
                    new_board = Board(new_grid_after_move)
                    eat_positions = new_board.can_piece_eat_return_eat_positions(piece)
                    if eat_positions:
                        for eat_pos in eat_positions:
                            eat_move = CheckersMove(piece.x, piece.y, eat_pos[0], eat_pos[1], True)
                            if is_move_eating_my_piece(eat_move, new_grid_after_move): return True
    moved_piece.is_flagged = False
    return False


def is_in_danger_after_move(new_grid_after_move, move):
    moved_piece = new_grid_after_move[move.end_x][move.end_y]
    for row in new_grid_after_move:
        for piece in row:
            if piece:
                if piece.owner != moved_piece.owner:
                    from Board import Board
                    new_board = Board(new_grid_after_move)
                    eat_positions = new_board.can_piece_eat_return_eat_positions(piece)
                    if eat_positions:
                        return True
    return False


def is_eat_move_from_king(move, grid):
    piece = grid[move.start_x][move.start_y]
    opponentpiece_encountered = False
    eaten_piece = None
    min_x = min(move.start_x, move.end_x)
    max_x = max(move.start_x, move.end_x)
    min_y = min(move.start_y, move.end_y)
    max_y = max(move.start_y, move.end_y)
    for col in range(min_x + 1, max_x):
        for row in range(min_y + 1, max_y):
            if abs(col - move.end_x) == abs(row - move.end_y):
                current_square = grid[col][row]
                if current_square:
                    if current_square.owner.color == piece.owner.color:
                        return False, None
                    else:
                        if opponentpiece_encountered:
                            return False, None
                        opponentpiece_encountered = True
                        eaten_piece = (current_square.x, current_square.y)
    return opponentpiece_encountered, eaten_piece


def algo_no_danger_for_moved(moves, board):
    for move in moves:
        new_grid_after_move = get_new_grid_from_move(move, board)
        moved_piece = new_grid_after_move[move.end_x][move.end_y]
        moved_piece.is_flagged = True
        move.is_danger_move = is_moved_piece_in_danger(new_grid_after_move, move)
        if not move.is_danger_move:
            chosen_move = move
            return chosen_move


def algo_no_danger(moves, board):
    for move in moves:
        new_grid_after_move = get_new_grid_from_move(move, board)
        move.is_danger_move = is_in_danger_after_move(new_grid_after_move, move)
        if not move.is_danger_move:
            chosen_move = move
            return chosen_move


def algo_no_danger_random(moves, board):
    for move in moves:
        new_grid_after_move = get_new_grid_from_move(move, board)
        moved_piece = new_grid_after_move[move.end_x][move.end_y]
        moved_piece.is_flagged = True
        move.is_danger_move = is_moved_piece_in_danger(new_grid_after_move, move)
    non_danger_moves = [move for move in moves if not move.is_danger_move]
    if non_danger_moves:
        random_element = random.choice(non_danger_moves)
        return random_element
    if moves:
        move = moves[0]
        return move


def algo_first(moves, board):
    return moves[0]


def algo_random(moves):
    random_element = random.choice(moves)
    return random_element


def get_new_grid_from_move(move, board):
    piece = board.get_piece([move.start_x, move.start_y])
    piece.is_flagged = True
    new_grid = deepcopy(board.grid)
    # simple eat move
    if not piece.is_king and (abs(move.start_x - move.end_x) > 1 or abs(move.start_y - move.end_y) > 1):
        eaten_piece_x = int((move.start_x + move.end_x) / 2)
        eaten_piece_y = int((move.start_y + move.end_y) / 2)
        new_grid[eaten_piece_x][eaten_piece_y] = None
        new_grid[move.end_x][move.end_y] = piece
        new_grid[move.start_x][move.start_y] = None

    elif piece.is_king:
        is_eat_move, eaten_piece_coor = is_eat_move_from_king(move, board.grid)
        if is_eat_move:
            eaten_piece = board.grid[eaten_piece_coor[0]][eaten_piece_coor[1]]
            new_grid[eaten_piece.x][eaten_piece.y] = None
            new_grid[move.end_x][move.end_y] = piece
            new_grid[move.start_x][move.start_y] = None
        else:
            # simple king move
            new_grid[move.end_x][move.end_y] = piece
            new_grid[move.start_x][move.start_y] = None
    else:
        # simple move
        new_grid[move.end_x][move.end_y] = piece
        new_grid[move.start_x][move.start_y] = None
    return new_grid


class BotPlayer(Player):
    def __init__(self, name, color, direction, captured_pieces: int, algo_name='random'):
        super().__init__(name, color, direction, captured_pieces)
        self.piece_that_just_ate = None
        self.algo_name = algo_name

    def make_play_decision(self, board, game_state):
        moves = self.get_available_moves(board, game_state)
        chosen_move = None
        if not moves: return None

        if moves[0].is_eat_move:
            eat_moves = [move for move in moves if move.is_eat_move]
            moves = eat_moves
        if self.algo_name == "random":
            chosen_move = algo_random(moves)
        if self.algo_name == "first":
            chosen_move = algo_first(moves, board)
        if self.algo_name == "no_danger_for_moved":
            chosen_move = algo_no_danger_for_moved(moves, board)
        if self.algo_name == "no_danger_random":
            chosen_move = algo_no_danger_random(moves, board)
        if self.algo_name == "no_danger":
            chosen_move = algo_no_danger(moves, board)
        first_move = moves[0] if moves else None
        chosen_move = first_move if not chosen_move else chosen_move
        if chosen_move:
            if chosen_move.is_eat_move:
                self.piece_that_just_ate = (chosen_move.end_x, chosen_move.end_y)
            else:
                self.piece_that_just_ate = None
        return chosen_move

    def get_available_moves(self, board, game_state):
        available_moves = []
        if self.piece_that_just_ate:
            piece_obj = board.get_piece(self.piece_that_just_ate)
            if piece_obj:
                eat_again_positions = board.can_piece_eat_return_eat_positions(piece_obj, all_directions=True)
                if eat_again_positions:
                    available_moves.append(CheckersMove(self.piece_that_just_ate[0], self.piece_that_just_ate[1],
                                                        eat_again_positions[0][0], eat_again_positions[0][1], True))
                    return available_moves
        # Check if there are pieces that can eat
        if game_state.pieces_that_can_eat:
            # If there are pieces that can eat, prioritize those moves
            for piece in game_state.pieces_that_can_eat:
                # Get possible next positions for the selected piece
                piece_obj = board.get_piece(piece)
                possible_next_positions = board.get_selected_piece_possible_next_positions(piece_obj, only_eat_pos=True)
                for position in possible_next_positions:
                    available_moves.append(CheckersMove(piece_obj.x, piece_obj.y, position[0], position[1], True))
        else:
            for row in board.grid:
                for piece in row:
                    if piece and piece.owner == game_state.player_turn:
                        possible_next_positions = board.get_selected_piece_possible_next_positions(piece,
                                                                                                   is_king=piece.is_king)
                        for position in possible_next_positions:
                            available_moves.append(CheckersMove(piece.x, piece.y, position[0], position[1], False))
        return available_moves
