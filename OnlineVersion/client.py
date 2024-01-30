import constants
from CurrentPlaySituation import CurrentPlaySituation
import pygame
import socket
import json
import sys
import pickle

text = "."


class CheckersClient:
    def __init__(self):
        self.all_players_are_connected = False
        self.text = ""
        self.width = constants.WIDTH
        self.height = constants.HEIGHT
        self.up_left = (constants.MARGIN, constants.MARGIN)
        self.down_right = (
            min(self.width, self.height) - constants.MARGIN, min(self.width, self.height) - constants.MARGIN)
        self.square_size = (self.down_right[0] - self.up_left[0]) / constants.SIZE_BOARD
        self.current_play_situation = CurrentPlaySituation(None, None, None, None, None, None, None, None, None)
        self.square_size = (self.down_right[0] - self.up_left[0]) / constants.SIZE_BOARD

    def start_client(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((constants.IP_ADDRESS_CLIENT, constants.PORT))

        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.client.send(b'{"type" : "request_name"}')
        data = self.client.recv(8192 * 2 * 2).decode()
        pygame.display.set_caption(f"{data}'s Game")
        clock = pygame.time.Clock()


        self.running = True
        while self.running:
            if self.current_play_situation.player1:
                self.screen.fill(constants.WHITE)
                self.draw_board()
                self.draw_dots()
                self.draw_score()
            if self.current_play_situation.nbr_of_players != 2:
                self.draw_waiting_screen()
            else:
                self.all_players_are_connected = True

            self.handle_events()
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

if __name__ == "__main__":
    client = CheckersClient()
    client.start_client()
