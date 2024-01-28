import pygame

import sys

import settings


def click_in_board(given_point, up_left, down_right):
    return up_left[0] <= given_point[0] <= down_right[0] and up_left[1] <= given_point[1] <= down_right[1]


class Checkers:
    def __init__(self):
        # Initialize Pygame
        self.chess_pions = []
        pygame.init()

        # Set up the screen
        self.width, self.height = 1000, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Chekcers")
        self.up_left = (settings.MARGIN, settings.MARGIN)
        self.down_right = (
            min(self.width, self.height) - settings.MARGIN, min(self.width, self.height) - settings.MARGIN)
        self.square_size = (self.down_right[0] - self.up_left[0]) / settings.SIZE_BOARD
        self.board = [[1, -1, 1, -1, 1, -1, 1, -1],
                      [-1, 1, -1, 1, -1, 1, -1, 1],
                      [1, -1, 1, -1, 1, -1, 1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1, -1],
                      [-1, 0, -1, 0, -1, 0, -1, 0],
                      [0, -1, 0, -1, 0, -1, 0, -1],
                      [-1, 0, -1, 0, -1, 0, -1, 0]]

        # List to store dots' positions
        self.dots = []

        # Set up the clock
        self.clock = pygame.time.Clock()
        self.game_state = 0
        self.selected_dot = (-1, -1)

    def draw_board(self):
        margin = settings.MARGIN
        board_height = min([self.width, self.height]) - 2 * margin

        for j in range(settings.SIZE_BOARD):
            for i in range(8):
                if (j + i) % 2 == 0 and i < 8:
                    pygame.draw.rect(self.screen, settings.BROWN, (
                        margin + self.square_size * i, margin + self.square_size * j, self.square_size,
                        self.square_size))

        for i in range(9):
            start_pos_vertical = (margin + (board_height / 8) * i, margin)
            end_pos_vertical = (margin + board_height / 8 * i, board_height + margin)
            pygame.draw.line(self.screen, settings.BOARD_COLOR, start_pos_vertical, end_pos_vertical,
                             settings.BOARD_LINE_WIDTH)
            start_pos_horizontal = (margin, margin + (board_height / 8) * i)
            end_pos_horizontal = (board_height + margin, board_height / 8 * i + margin)
            pygame.draw.line(self.screen, settings.BOARD_COLOR, start_pos_horizontal, end_pos_horizontal,
                             settings.BOARD_LINE_WIDTH)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if click_in_board((x, y), self.up_left, self.down_right):
                    selected_x, selected_y = self.detect_click_zone(x, y)
                    print(selected_x, selected_y)
                    self.player_clicked(selected_x, selected_y)
                self.dots.append((x, y))

    def draw_dots(self):
        for y, row in enumerate(self.board):
            for x, col in enumerate(row):
                if col == 0:
                    dot = self.position_to_coordinates(x, y)
                    pygame.draw.circle(self.screen, settings.PLAYER_1_COLOR, dot, self.square_size / 2 - 5)
                    pygame.draw.circle(self.screen, settings.BLACK, dot, self.square_size / 2 - 5, 3)
                if col == 1:
                    dot = self.position_to_coordinates(x, y)
                    pygame.draw.circle(self.screen, settings.PLAYER_2_COLOR, dot, self.square_size / 2 - 5)
                    pygame.draw.circle(self.screen, settings.BLACK, dot, self.square_size / 2 - 5, 3)

        for dot in self.chess_pions:
            pygame.draw.circle(self.screen, settings.WHITE, dot, self.square_size / 2 - 5)

    def run_game(self):
        while True:
            self.handle_events()
            self.screen.fill(settings.WHITE)
            self.draw_board()
            self.draw_dots()

            # Update the display
            pygame.display.flip()

            # Control the frames per second (FPS)
            self.clock.tick(60)

    def detect_click_zone(self, x, y):
        select_square_x = int(((x - settings.MARGIN) / (self.down_right[0] - settings.MARGIN)) * 8)
        select_square_y = int(((y - settings.MARGIN) / (self.down_right[1] - settings.MARGIN)) * 8)
        return select_square_x, select_square_y

    def position_to_coordinates(self, selected_x, selected_y):
        coordinate_x = selected_x * self.square_size + settings.MARGIN + self.square_size / 2
        coordinate_y = selected_y * self.square_size + settings.MARGIN + self.square_size / 2
        # self.chess_pions.append((coordinate_x, coordinate_y))
        return coordinate_x, coordinate_y

    def player_clicked(self, selected_x, selected_y):
        if self.game_state == self.board[selected_y][selected_x]:
            print(self.game_state, "WAW", self.board[selected_y][selected_x])


if __name__ == "__main__":
    checkers = Checkers()
    checkers.run_game()
