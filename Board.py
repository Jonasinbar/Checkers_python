import operator

import constants
from Piece import Piece
from Player import Player


class Board:
    def __init__(self, grid=None):
        if not grid:
            self.grid = [[None for _ in range(constants.SIZE_BOARD)] for _ in range(constants.SIZE_BOARD)]
        else:
            self.grid = grid

    def put_pieces_start_config(self, player1: Player, player2: Player):
        size = len(self.grid)
        for y in range(size):
            for x in range(size):
                if y < constants.NUMBER_OF_LINES_OF_DOTS_IN_START and (y + x) % 2 != 0:
                    self.grid[x][y] = Piece(player2, x, y)
                if y >= size - constants.NUMBER_OF_LINES_OF_DOTS_IN_START and (y + x) % 2 != 0:
                    self.grid[x][y] = Piece(player1, x, y)

    def print_board(self):
        size = len(self.grid)
        for y in range(size):
            for x in range(size):
                if self.grid[x][y] is None:
                    print("XXXXXXX", end=" ")
                else:
                    print(self.grid[x][y].owner.name, end=" ")  # Assuming Piece class has a symbol attribute
            print()

    def put_pieces_start_config_test(self, player1: Player, player2: Player):
        self.grid[1][6] = Piece(player1, 1, 6)
        self.grid[2][7] = Piece(player2, 2, 7)
        self.grid[1][0] = Piece(player1, 1, 0)
        self.grid[0][5] = Piece(player1, 0, 5)
        self.grid[0][3] = Piece(player2, 0, 3)
        # self.grid[1][6] = Piece(player1, 1, 6)
        # self.grid[3][4] = Piece(player1, 3, 4)
        # self.grid[2][5] = Piece(player2, 2, 5)
        self.grid[4][3] = Piece(player2, 4, 3)
        self.grid[6][5] = Piece(player1, 6, 5)

    def test_represent(self):
        size = len(self.grid)
        for y in range(size):
            for x in range(size):
                if self.grid[x][y]:
                    y = self.grid[x][y].y
                    x = self.grid[x][y].x
                    print(str(y) + "," + str(x), end=" ")
                else:
                    print("NO", end=" ")
            print()

    def get_piece(self, selected_square):
        return self.grid[selected_square[0]][selected_square[1]]

    def position_is_in_board(self, position):
        x, y = position
        size = len(self.grid)
        return 0 <= x < size and 0 <= y < size

    def click_in_board(self, given_point):
        return constants.UP_LEFT[0] <= given_point[0] <= constants.DOWN_RIGHT[0] and constants.UP_LEFT[1] <= given_point[1] <= \
            constants.DOWN_RIGHT[1]

    def detect_square_position_from_click(self, x, y):
        select_square_x = int(((x - constants.MARGIN) / (constants.DOWN_RIGHT[0] - constants.MARGIN)) * constants.SIZE_BOARD)
        select_square_y = int(((y - constants.MARGIN) / (constants.DOWN_RIGHT[1] - constants.MARGIN)) * constants.SIZE_BOARD)
        return select_square_x, select_square_y

    @staticmethod
    def position_to_coordinates(selected_dot):
        coordinate_x = selected_dot[0] * constants.SQUARE_SIZE + constants.MARGIN + constants.SQUARE_SIZE / 2
        coordinate_y = selected_dot[1] * constants.SQUARE_SIZE + constants.MARGIN + constants.SQUARE_SIZE / 2
        return coordinate_x, coordinate_y

    def get_pieces_that_can_eat(self, players_turn):
        pieces_that_can_eat = []
        for row in self.grid:
            for piece in row:
                if piece and piece.owner == players_turn:
                    if piece.is_king:
                        eat_pos = self.can_piece_eat_return_eat_positions_for_king(piece)
                    else:
                        eat_pos = self.can_piece_eat_return_eat_positions(piece)
                    if eat_pos:
                        pieces_that_can_eat.append((piece.x, piece.y))
        return pieces_that_can_eat

    def get_possible_position_and_eat_for_king(self, start_x, start_y, x_direction, y_direction, limit):
        opposite_piece_encountered = False
        possible_positions = []
        eat_positions = []

        start_piece = self.get_piece((start_x, start_y))
        for i in range(1, limit + 1):
            current_square = self.get_piece((x_direction(start_x, i), y_direction(start_y, i)))
            if current_square:
                if current_square.owner.color == start_piece.owner.color:
                    return possible_positions, eat_positions
                else:
                    if opposite_piece_encountered:
                        return possible_positions, eat_positions
                    opposite_piece_encountered = True
            elif opposite_piece_encountered:
                eat_positions.append((x_direction(start_x, i), y_direction(start_y, i)))

            possible_positions.append((x_direction(start_x, i), y_direction(start_y, i)))
        return possible_positions, eat_positions

    def can_piece_eat_return_eat_positions(self, current_piece, all_directions=False):
        if current_piece.is_king:
            eat_pos_for_king = self.can_piece_eat_return_eat_positions_for_king(current_piece)
            if eat_pos_for_king: return eat_pos_for_king
        eat_positions = []
        opponent_color = constants.PLAYER_1_COLOR if current_piece.owner.color == constants.PLAYER_2_COLOR else constants.PLAYER_2_COLOR
        if current_piece.owner.direction == constants.UP_DIRECTION or all_directions:
            up_left = (current_piece.x - 1, current_piece.y - 1)
            up_left_eat = (current_piece.x - 2, current_piece.y - 2)
            up_right = (current_piece.x + 1, current_piece.y - 1)
            up_right_eat = (current_piece.x + 2, current_piece.y - 2)
            if self.position_is_in_board(up_right) and self.get_piece(up_right):
                if self.position_is_in_board(up_right_eat) and not self.get_piece(up_right_eat) and self.get_piece(
                        up_right).owner.color == opponent_color:
                    eat_positions.append(up_right_eat)
            if self.position_is_in_board(up_left) and self.get_piece(up_left):
                if self.position_is_in_board(up_left_eat) and not self.get_piece(up_left_eat) and self.get_piece(
                        up_left).owner.color == opponent_color:
                    eat_positions.append(up_left_eat)

        if current_piece.owner.direction == constants.DOWN_DIRECTION or all_directions:
            down_left = (current_piece.x - 1, current_piece.y + 1)
            down_left_eat = (current_piece.x - 2, current_piece.y + 2)
            down_right = (current_piece.x + 1, current_piece.y + 1)
            down_right_eat = (current_piece.x + 2, current_piece.y + 2)
            if self.position_is_in_board(down_right) and self.get_piece(down_right):
                if self.position_is_in_board(down_right_eat) and not self.get_piece(down_right_eat) and self.get_piece(
                        down_right).owner.color == opponent_color:
                    eat_positions.append(down_right_eat)
            if self.position_is_in_board(down_left) and self.get_piece(down_left):
                if self.position_is_in_board(down_left_eat) and not self.get_piece(down_left_eat) and self.get_piece(
                        down_left).owner.color == opponent_color:
                    eat_positions.append(down_left_eat)
        return eat_positions

    def can_piece_eat_return_eat_positions_for_king(self, selected_piece):
        up_lefts = self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                               x_direction=operator.sub, y_direction=operator.sub,
                                                               limit=min(selected_piece.x, selected_piece.y))[1]
        up_rights = self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                                x_direction=operator.add, y_direction=operator.sub,
                                                                limit=min(len(self.grid) - 1 - selected_piece.x,
                                                                          selected_piece.y))[1]
        down_lefts = self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                                 x_direction=operator.sub, y_direction=operator.add,
                                                                 limit=min(selected_piece.x,
                                                                           len(self.grid) - 1 - selected_piece.y))[1]
        down_rights = self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                                  x_direction=operator.add, y_direction=operator.add,
                                                                  limit=min(len(self.grid) - 1 - selected_piece.x,
                                                                            len(self.grid) - 1 - selected_piece.y))[1]
        return up_rights + up_lefts + down_lefts + down_rights

    @staticmethod
    def check_and_set_if_is_king(grid, selected_x, selected_y):
        try:
            piece = grid[selected_x][selected_y]
        except Exception as e:
            print(selected_x, selected_y, "error")
            raise e
        if piece:
            if piece.owner.direction == constants.UP_DIRECTION and selected_y == 0:
                piece.is_king = True
            if piece.owner.direction == constants.DOWN_DIRECTION and selected_y == constants.SIZE_BOARD - 1:
                piece.is_king = True

    def get_selected_piece_possible_next_positions(self, selected_piece, only_eat_pos=False, all_directions=False,
                                                   is_king=False):
        selected_piece_move_options = []
        if selected_piece:
            eat_positions = self.can_piece_eat_return_eat_positions(selected_piece, all_directions=all_directions)

            if len(eat_positions) > 0:
                selected_piece_move_options.extend(eat_pos for eat_pos in eat_positions)
                return selected_piece_move_options
            if (
                    selected_piece.owner.direction == constants.UP_DIRECTION or all_directions or is_king) and not only_eat_pos:
                up_lefts = [(selected_piece.x - 1, selected_piece.y - 1)] if not is_king else \
                self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                            x_direction=operator.sub, y_direction=operator.sub,
                                                            limit=min(selected_piece.x, selected_piece.y))[0]
                up_rights = [(selected_piece.x + 1, selected_piece.y - 1)] if not is_king else \
                self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                            x_direction=operator.add, y_direction=operator.sub,
                                                            limit=min(len(self.grid) - 1 - selected_piece.x,
                                                                      selected_piece.y))[0]
                for up_right in up_rights:
                    if self.position_is_in_board(up_right) and not self.get_piece(up_right):
                        selected_piece_move_options.append(up_right)
                for up_left in up_lefts:
                    if self.position_is_in_board(up_left) and not self.get_piece(
                            up_left): selected_piece_move_options.append(up_left)

            if (
                    selected_piece.owner.direction == constants.DOWN_DIRECTION or all_directions or is_king) and not only_eat_pos:
                down_lefts = [(selected_piece.x - 1, selected_piece.y + 1)] if not is_king else \
                    self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                                x_direction=operator.sub, y_direction=operator.add,
                                                                limit=min(selected_piece.x,
                                                                          len(self.grid) - 1 - selected_piece.y))[0]
                down_rights = [(selected_piece.x + 1, selected_piece.y + 1)] if not is_king else \
                    self.get_possible_position_and_eat_for_king(start_x=selected_piece.x, start_y=selected_piece.y,
                                                                x_direction=operator.add, y_direction=operator.add,
                                                                limit=min(len(self.grid) - 1 - selected_piece.x,
                                                                          len(self.grid) - 1 - selected_piece.y))[0]
                for down_right in down_rights:
                    if self.position_is_in_board(down_right) and not self.get_piece(down_right):
                        selected_piece_move_options.append(down_right)
                for down_left in down_lefts:
                    if self.position_is_in_board(down_left) and not self.get_piece(down_left):
                        selected_piece_move_options.append(down_left)
        return selected_piece_move_options
