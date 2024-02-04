import pickle

import constants
from Board import Board
from Game import Game
import socket
import threading
import json
import CurrentPlaySituation
from CurrentPlaySituation import CurrentPlaySituation


class CheckersServer:

    def __init__(self):
        self.clients = {}
        self.nbr_of_players = 0
        self.game = Game("Player1", "Player2", local_mode=False)

    def handle_client(self, client_socket, player_name):
        while True:
            try:
                data = client_socket.recv(8192 * 2 * 2).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                self.handle_game_message(player_name, message, client_socket)
            except Exception as e:
                print(f"Error handling client {player_name}: {e}")
                break
        client_socket.close()

    def handle_game_message(self, player_name, message, client_socket):
        if message['type'] == 'request_name':
            self.clients[player_name].send(player_name.encode())

        if message['type'] == 'request_settings':
            data_settings = {
                'SIZE_BOARD': constants.SIZE_BOARD,
                'NUMBER_OF_LINES_OF_DOTS_IN_START': constants.NUMBER_OF_LINES_OF_DOTS_IN_START,
                'PLAYER_1_COLOR': constants.PLAYER_1_COLOR,
                'PLAYER_2_COLOR': constants.PLAYER_2_COLOR,
            }
            self.clients[player_name].send(json.dumps(data_settings).encode())

        if message['type'] == 'click':
            if player_name == self.game.game_state.player_turn.name:
                x, y = message['position']
                if self.game.board.click_in_board((x, y)):
                    if not self.game.game_state.winner:
                        selected_x, selected_y = self.game.board.detect_square_position_from_click(x, y)
                        self.game.handle_click_on_square(selected_x, selected_y)
                        self.game.game_state.pieces_that_can_eat = self.game.board.get_pieces_that_can_eat(
                            self.game.game_state.player_turn)
                        self.game.detect_if_winner()

        if message['type'] == 'request_dots':
            # Send the current game state to the client
            grid = self.game.board.grid  # pickle.dumps(self.board.grid)
            selected_piece_move_options = self.game.game_state.selected_piece_move_options
            player_turn = self.game.game_state.player_turn
            self.check_all_pieces_if_is_king()
            current_play_situation = CurrentPlaySituation(grid, self.game.player1, self.game.player2,
                                                          selected_piece_move_options,
                                                          self.game.game_state.selected_piece,
                                                          self.game.game_state.pieces_that_can_eat, player_turn,
                                                          self.game.game_state.winner, self.nbr_of_players)
            current_play_state_for_client = pickle.dumps(current_play_situation)

            client_socket.send(current_play_state_for_client)

    def check_all_pieces_if_is_king(self):
        for row in self.game.board.grid:
            for piece in row:
                if getattr(piece, "owner", None):
                    Board.check_and_set_if_is_king(self.game.board.grid, piece.x, piece.y)

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((constants.IP_ADDRESS_SERVER, constants.PORT))
        server.listen(2)  # Allow 2 players to connect
        print(f"Server listening on port {constants.PORT}...")
        player_name = "Player1"
        while self.nbr_of_players < 2:
            client, addr = server.accept()
            print(f"Player {player_name} connected from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client, player_name))
            client_handler.start()
            self.clients[player_name] = client
            self.nbr_of_players += 1
            player_name = "Player2"


if __name__ == "__main__":
    server = CheckersServer()
    server.start_server()
