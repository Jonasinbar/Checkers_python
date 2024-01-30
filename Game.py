import operator
import sys

import pygame

import constants
from Board import Board
from GameState import GameState
from Player import Player


class Game:
    def __init__(self, player1_name, player2_name, local_mode=True):
        self.player1 = Player(player1_name, constants.PLAYER_1_COLOR, constants.PLAYER_1_DIRECTION, 0)
        self.player2 = Player(player2_name, constants.PLAYER_2_COLOR, constants.PLAYER_2_DIRECTION, 0)
        self.board = Board()
        self.board.put_pieces_start_config(self.player1, self.player2)
        self.game_state = GameState(self.player1, None, [], [], None)
        if local_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((constants.WIDTH, constants.HEIGHT))
            pygame.display.set_caption("Chekcers")
            self.clock = pygame.time.Clock()

    def run_game(self):
        while True:
            self.screen.fill(constants.WHITE)
            self.draw_board(self.screen)
            self.draw_dots()
            self.draw_score()
            self.handle_events()

            # Update the display
            pygame.display.flip()

            # Control the frames per second (FPS)
            self.clock.tick(10)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                print("absolute:", x, y)
                if self.board.click_in_board((x, y)):
                    if not self.game_state.winner:
                        selected_x, selected_y = self.board.detect_square_position_from_click(x, y)
                        print("selected_x : ", selected_x, "selected_y", selected_y)
                        self.handle_click_on_square(selected_x, selected_y)
                        self.game_state.pieces_that_can_eat = self.board.get_pieces_that_can_eat(
                            self.game_state.player_turn)
                        self.detect_if_winner()

    @staticmethod
    def draw_board(screen):
        margin = constants.MARGIN
        board_height = min([constants.WIDTH, constants.HEIGHT]) - 2 * margin

        for j in range(constants.SIZE_BOARD):
            for i in range(constants.SIZE_BOARD):
                if (j + i) % 2 != 0 and i < constants.SIZE_BOARD:
                    pygame.draw.rect(screen, constants.BROWN, (
                        margin + constants.SQUARE_SIZE * i, margin + constants.SQUARE_SIZE * j,
                        constants.SQUARE_SIZE, constants.SQUARE_SIZE))

        for i in range(constants.SIZE_BOARD + 1):
            start_pos_vertical = (margin + (board_height / constants.SIZE_BOARD) * i, margin)
            end_pos_vertical = (margin + board_height / constants.SIZE_BOARD * i, board_height + margin)
            pygame.draw.line(screen, constants.BOARD_COLOR, start_pos_vertical, end_pos_vertical,
                             constants.BOARD_LINE_WIDTH)
            start_pos_horizontal = (margin, margin + (board_height / constants.SIZE_BOARD) * i)
            end_pos_horizontal = (board_height + margin, board_height / constants.SIZE_BOARD * i + margin)
            pygame.draw.line(screen, constants.BOARD_COLOR, start_pos_horizontal, end_pos_horizontal,
                             constants.BOARD_LINE_WIDTH)

    def draw_dots(self):
        for y in range(constants.SIZE_BOARD):
            for x in range(constants.SIZE_BOARD):
                if self.board.grid[x][y]:
                    self.board.check_and_set_if_is_king(x, y)
                    piece_position = self.board.position_to_coordinates((x, y))
                    pygame.draw.circle(self.screen, self.board.grid[x][y].owner.color, piece_position,
                                       self.board.square_size / 2 - 5)
                    pygame.draw.circle(self.screen, constants.BLACK, piece_position, self.board.square_size / 2 - 5, 3)
                    if self.board.grid[x][y].is_king: self.draw_crown(piece_position)
        if self.game_state.selected_piece:
            selected_color = constants.PLAYER_1_COLOR_SELECTED if self.game_state.selected_piece.owner.color == constants.PLAYER_1_COLOR else constants.PLAYER_2_COLOR_SELECTED
            piece_position = self.board.position_to_coordinates(
                (self.game_state.selected_piece.x, self.game_state.selected_piece.y))
            pygame.draw.circle(self.screen, selected_color, piece_position,
                               self.board.square_size / 2 - 5 - 3)
            if self.game_state.selected_piece.is_king: self.draw_crown(piece_position)
        if len(self.game_state.selected_piece_move_options) > 0:
            for move_option in self.game_state.selected_piece_move_options:
                pygame.draw.circle(self.screen, constants.GREY, self.board.position_to_coordinates(move_option),
                                   self.board.square_size / 2 - 5 - 3)
        for piece_that_can_eat in self.game_state.pieces_that_can_eat:
            pygame.draw.circle(self.screen, constants.BLACK, self.board.position_to_coordinates(piece_that_can_eat),
                               self.board.square_size / 2 - 5 - 7, 1)

    def handle_click_on_square(self, selected_x, selected_y):
        piece_clicked = self.board.get_piece((selected_x, selected_y))
        if piece_clicked:
            not_your_turn = self.game_state.player_turn != piece_clicked.owner
            you_have_to_eat = len(self.game_state.pieces_that_can_eat) > 0 and (
                piece_clicked.x, piece_clicked.y) not in self.game_state.pieces_that_can_eat
            if self.game_state.piece_that_have_to_eat_again:
                if self.game_state.piece_that_have_to_eat_again == self.game_state.selected_piece:
                    # do nothing until you do the eat move
                    print("do nothing")
                    return
            if not_your_turn or you_have_to_eat:
                self.reset_selected_piece()
                return

            self.game_state.selected_piece = piece_clicked
            self.game_state.selected_piece_move_options = self.board.get_selected_piece_possible_next_positions(
                self.game_state.selected_piece, is_king=piece_clicked.is_king)
        # Move selection
        elif (selected_x, selected_y) in self.game_state.selected_piece_move_options:
            is_eat_move, eaten_piece = self.is_eat_move(selected_x, selected_y)
            eaten_piece_by_king = (
                eaten_piece[0], eaten_piece[1]) if is_eat_move and self.game_state.selected_piece.is_king else None
            if is_eat_move:
                print("EAT MOVE")
                self.make_eat_move(selected_x, selected_y, eaten_piece_by_king=eaten_piece_by_king)
                if self.board.can_piece_eat_return_eat_positions(self.game_state.selected_piece, all_directions=True):
                    print('CAN EAT AGAIN')
                    self.game_state.pieces_that_can_eat = []  # self.board.get_pieces_that_can_eat(self.game_state.player_turn)
                    self.game_state.selected_piece_move_options = self.board.get_selected_piece_possible_next_positions(
                        self.game_state.selected_piece, only_eat_pos=True, all_directions=True)
                    print('can eat next position', self.game_state.selected_piece_move_options)
                    self.game_state.piece_that_have_to_eat_again = self.game_state.selected_piece
                else:
                    self.game_state.selected_piece = None
                    self.game_state.selected_piece_move_options = []
                    self.game_state.pieces_that_can_eat = []
                    self.game_state.piece_that_have_to_eat_again = None
                    self.change_player_turn()
                return

            self.board.grid[self.game_state.selected_piece.x][self.game_state.selected_piece.y] = None
            self.game_state.selected_piece.x = selected_x
            self.game_state.selected_piece.y = selected_y
            self.board.grid[selected_x][selected_y] = self.game_state.selected_piece
            self.game_state.selected_piece = None
            self.game_state.selected_piece_move_options = []
            self.game_state.pieces_that_can_eat = []
            self.game_state.piece_that_have_to_eat_again = None
            self.change_player_turn()
        # Reset,
        else:
            # just make sure that we are not in a just eat and can eat again situation
            if not self.game_state.piece_that_have_to_eat_again:
                self.reset_selected_piece()

    def draw_score(self):
        pygame.font.init()
        my_font = pygame.font.SysFont('Comic Sans MS', 30)

        player1_text_surface = my_font.render(self.player1.name, False, self.player1.color)
        player2_text_surface = my_font.render(self.player2.name, False, self.player2.color)

        player1_score_x = self.board.square_size * constants.SIZE_BOARD + constants.MARGIN * 2
        player2_score_x = player1_score_x + len(self.player1.name) * 30 + constants.MARGIN * 2

        player1_score_text_surface = my_font.render(str(self.player1.captured_pieces), False, (0, 0, 0))
        player2_score_text_surface = my_font.render(str(self.player2.captured_pieces), False, (0, 0, 0))

        current_player_x = player1_score_x if self.game_state.player_turn == self.player1 else player2_score_x

        winner_text_surface = None
        if self.game_state.winner:
            winner_text_surface = my_font.render(self.game_state.winner.name + " is the Winner !!", False, (0, 0, 0))

        # Draw player names and scores
        self.screen.blit(player1_text_surface, (player1_score_x, self.player1.captured_pieces))
        self.screen.blit(player2_text_surface, (player2_score_x, self.player2.captured_pieces))
        self.screen.blit(player1_score_text_surface, (player1_score_x, 60))
        self.screen.blit(player2_score_text_surface, (player2_score_x, 60))

        # Highlight current player
        pygame.draw.rect(self.screen, constants.BLACK, (current_player_x - 5, 0, 120, 60), 2)

        # Draw winner message
        if winner_text_surface:
            winner_x = player1_score_x if self.game_state.winner == self.player1 else player2_score_x
            winner_x += len(self.player1.name) * 30
            self.screen.blit(winner_text_surface, (winner_x, 180))

    def reset_selected_piece(self):
        self.game_state.selected_piece = None
        self.game_state.selected_piece_move_options = []

    def change_player_turn(self):
        self.game_state.player_turn = self.player2 if self.game_state.player_turn == self.player1 else self.player1

    def make_eat_move(self, selected_x, selected_y, eaten_piece_by_king=None):
        self.board.grid[self.game_state.selected_piece.x][self.game_state.selected_piece.y] = None
        eaten_piece_x = int((self.game_state.selected_piece.x + selected_x) / 2)
        eaten_piece_y = int((self.game_state.selected_piece.y + selected_y) / 2)
        if eaten_piece_by_king:
            eaten_piece_x = eaten_piece_by_king[0]
            eaten_piece_y = eaten_piece_by_king[1]
        self.board.grid[eaten_piece_x][eaten_piece_y] = None
        self.game_state.player_turn.captured_pieces += 1
        self.game_state.selected_piece.x = selected_x
        self.game_state.selected_piece.y = selected_y
        self.board.grid[selected_x][selected_y] = self.game_state.selected_piece

    def draw_crown(self, piece_position):
        imp = pygame.image.load(constants.CROWN_PATH).convert_alpha()
        crown_size = self.board.square_size * 0.8
        crown_small = pygame.transform.scale(imp, (crown_size, crown_size))
        crown_position = (piece_position[0] - crown_size / 2, piece_position[1] - crown_size / 2)
        self.screen.blit(crown_small, crown_position)

    def is_eat_move_from_king_return_eaten_piece(self, selected_x, selected_y):
        opponentpiece_encountered = False
        eaten_piece = None
        min_x = min(selected_x, self.game_state.selected_piece.x)
        max_x = max(selected_x, self.game_state.selected_piece.x)
        min_y = min(selected_y, self.game_state.selected_piece.y)
        max_y = max(selected_y, self.game_state.selected_piece.y)
        for col in range(min_x + 1, max_x):
            for row in range(min_y + 1, max_y):
                if abs(col - selected_x) == abs(row - selected_y):
                    current_square = self.board.get_piece((col, row))
                    if current_square:
                        if current_square.owner.color == self.game_state.selected_piece.owner.color:
                            return False, None
                        else:
                            if opponentpiece_encountered:
                                return False, None
                            opponentpiece_encountered = True
                            eaten_piece = (current_square.x, current_square.y)
        return opponentpiece_encountered, eaten_piece

    def is_eat_move(self, selected_x, selected_y):
        if not self.game_state.selected_piece.is_king and (
                abs(self.game_state.selected_piece.x - selected_x) > 1 or abs(
            self.game_state.selected_piece.y - selected_y) > 1):
            eaten_piece_x = int((self.game_state.selected_piece.x + selected_x) / 2)
            eaten_piece_y = int((self.game_state.selected_piece.y + selected_y) / 2)
            return True, (eaten_piece_x, eaten_piece_y)
        if self.game_state.selected_piece.is_king:
            return self.is_eat_move_from_king_return_eaten_piece(selected_x, selected_y)
        return False, None

    def detect_if_winner(self):
        number_of_player1_pieces = sum(1 for row in self.board.grid for piece in row if
                                       getattr(getattr(piece, "owner", None), "color", None) == self.player1.color)
        number_of_player2_pieces = sum(1 for row in self.board.grid for piece in row if
                                       getattr(getattr(piece, "owner", None), "color", None) == self.player2.color)
        if number_of_player1_pieces == 0 or number_of_player2_pieces == 0:
            self.game_state.winner = self.player1 if number_of_player2_pieces == 0 else self.player2
        if not self.can_player_make_one_move(self.player1):
            self.game_state.winner = self.player2
        if not self.can_player_make_one_move(self.player2):
            self.game_state.winner = self.player1

    def can_player_make_one_move(self, player):
        for row in self.board.grid:
            for piece in row:
                if getattr(piece, "owner", None) == player:
                    if len(self.board.get_selected_piece_possible_next_positions(piece, is_king=piece.is_king)):
                        return True
        return False


if __name__ == "__main__":
    game = Game("Player1", "Player2")
    game.run_game()
