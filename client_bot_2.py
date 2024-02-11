from CheckersMove import CheckersMove
import constants
import pygame
import socket
import json
import sys
import pickle

from Game import Game
from CurrentPlaySituation import CurrentPlaySituation

text = "."


def append_settings_from_server(settings_server):
    constants.SIZE_BOARD = settings_server["SIZE_BOARD"]
    constants.NUMBER_OF_LINES_OF_DOTS_IN_START = settings_server["NUMBER_OF_LINES_OF_DOTS_IN_START"]
    constants.PLAYER_1_COLOR = settings_server["PLAYER_1_COLOR"]
    constants.PLAYER_2_COLOR = settings_server["PLAYER_2_COLOR"]
    constants.SQUARE_SIZE = (constants.DOWN_RIGHT[0] - constants.UP_LEFT[0]) / constants.SIZE_BOARD


class CheckersClient:
    def __init__(self):
        self.all_players_are_connected = False
        self.piece_that_just_ate = None
        self.text = ""
        self.width = constants.WIDTH
        self.height = constants.HEIGHT
        self.up_left = (constants.MARGIN, constants.MARGIN)
        self.down_right = (
            min(self.width, self.height) - constants.MARGIN, min(self.width, self.height) - constants.MARGIN)
        self.current_play_situation = CurrentPlaySituation(None, None, None, None, None, None, None, None, None)

    def start_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((constants.IP_ADDRESS_CLIENT, constants.PORT))

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.client.send(b'{"type" : "request_name"}')
        data = self.client.recv(8192 * 2 * 2).decode()
        pygame.display.set_caption(f"{data}'s Game")
        self.name = data
        self.client.send(b'{"type" : "request_settings"}')
        data_settings = self.client.recv(8192 * 2 * 2).decode()
        append_settings_from_server(json.loads(data_settings))

        clock = pygame.time.Clock()


        self.running = True
        while self.running:
            if self.current_play_situation.player1:
                self.screen.fill(constants.WHITE)
                Game.draw_board(self.screen)
                Game.draw_dots(self.screen, self.current_play_situation.board.grid, self.current_play_situation.selected_piece, self.current_play_situation.selected_piece_move_options, self.current_play_situation.pieces_that_can_eat)
                Game.draw_score(self.screen, self.current_play_situation.player1, self.current_play_situation.player2, self.current_play_situation.player_turn, self.current_play_situation.winner)
            if self.current_play_situation.nbr_of_players != 2:
                self.draw_waiting_screen()
            else:
                self.all_players_are_connected = True

            self.handle_events()
            if self.current_play_situation.player_turn.name == self.name:
                move = self.get_bot_move()
                x, y = self.current_play_situation.board.position_to_coordinates((move.start_x, move.start_y))
                print(x, y)
                message_select = {
                    'type': 'click',
                    'position': (x, y),
                }
                if self.all_players_are_connected:
                    self.client.send(json.dumps(message_select).encode('utf-8'))

                # Request the latest game state from the server
                self.client.send(b'{"type" : "request_dots"}')
                data = self.client.recv(8192 * 2 * 2)
                self.current_play_situation = pickle.loads(data)

                x, y = self.current_play_situation.board.position_to_coordinates((move.end_x, move.end_y))
                print(x, y)
                message_move = {
                    'type': 'click',
                    'position': (x, y),
                }
                if self.all_players_are_connected:
                    self.client.send(json.dumps(message_move).encode('utf-8'))

            else:
                self.piece_that_just_ate = None
            # Request the latest game state from the server
            self.client.send(b'{"type" : "request_dots"}')
            data = self.client.recv(8192 * 2 * 2)
            self.current_play_situation = pickle.loads(data)


            pygame.display.flip()
            clock.tick(10)

        self.client.close()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                print(x, y)
                message = {
                    'type': 'click',
                    'position': (x, y),
                }
                if self.all_players_are_connected:
                    self.client.send(json.dumps(message).encode('utf-8'))

        # Request the latest game state from the server
        self.client.send(b'{"type" : "request_dots"}')
        data = self.client.recv(8192 * 2 * 2)
        self.current_play_situation = pickle.loads(data)

    def get_bot_move(self):
        moves = self.get_available_moves()
        for move in moves:
            print(move.start_x, move.start_y, move.end_x, move.end_y, move.is_eat_move)
        chosen_move = moves[0]
        if chosen_move.is_eat_move:
            self.piece_that_just_ate = (chosen_move.end_x, chosen_move.end_y)
        else:
            self.piece_that_just_ate = None
        # chosen_move = random.choice(moves)
        return chosen_move

    def get_available_moves(self):
        available_moves = []
        if self.piece_that_just_ate:
            piece_obj = self.current_play_situation.board.get_piece(self.piece_that_just_ate)
            if piece_obj:
                eat_again_positions = self.current_play_situation.board.can_piece_eat_return_eat_positions(piece_obj, all_directions=True)
                if eat_again_positions:
                    available_moves.append(CheckersMove(self.piece_that_just_ate[0], self.piece_that_just_ate[1], eat_again_positions[0][0], eat_again_positions[0][1], True))
                    return available_moves
        # Check if there are pieces that can eat
        if self.current_play_situation.pieces_that_can_eat:
            # If there are pieces that can eat, prioritize those moves
            for piece in self.current_play_situation.pieces_that_can_eat:
                # Get possible next positions for the selected piece
                piece_obj = self.current_play_situation.board.get_piece(piece)
                possible_next_positions = self.current_play_situation.board.get_selected_piece_possible_next_positions(piece_obj, only_eat_pos=True)
                for position in possible_next_positions:
                    available_moves.append(CheckersMove(piece_obj.x, piece_obj.y, position[0], position[1], True))
        else:
            for row in self.current_play_situation.board.grid:
                for piece in row:
                    if piece and piece.owner == self.current_play_situation.player_turn:
                        possible_next_positions = self.current_play_situation.board.get_selected_piece_possible_next_positions(piece)
                        for position in possible_next_positions:
                            available_moves.append(CheckersMove(piece.x, piece.y, position[0], position[1], False))
        return available_moves
    def draw_waiting_screen(self):
        if self.text == "..............":
            self.text = ""
        pygame.font.init()
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render("Waiting for other player to connect " + self.text, False,
                                      constants.BLACK)
        self.screen.blit(text_surface, (constants.WIDTH / 2, constants.HEIGHT / 2))
        self.text += "."


if __name__ == "__main__":
    client = CheckersClient()
    client.start_client()
