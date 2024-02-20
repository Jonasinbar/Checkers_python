class CheckersMove():
    def __init__(self, start_x, start_y, end_x, end_y, is_eat_move, is_danger_move=False):
        self.start_x = start_x
        self.start_y = start_y
        self.end_x = end_x
        self.end_y = end_y
        self.is_eat_move = is_eat_move
        self.is_danger_move = is_danger_move
