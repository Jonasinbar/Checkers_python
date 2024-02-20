from Game import Game


def make_n_games(n, algo1, algo2):
    wins_algo1 = 0
    wins_algo2 = 0

    for i in range(int(n/2)):
        game = Game(algo1, algo2, against_bot=True, is_simulation=True)
        game_state = game.run_game()
        if game_state.winner.name == algo1:
            wins_algo1 += 1
        else:
            wins_algo2 += 1
    for i in range(int(n/2)):
        game = Game(algo2, algo1, against_bot=True, is_simulation=True)
        game_state = game.run_game()
        if game_state.winner.name == algo1:
            wins_algo1 += 1
        else:
            wins_algo2 += 1
    print(algo1, wins_algo1, algo2, wins_algo2)
    # print(game_state.winner.name, "is the winner, ",
    #       max(game.player1.captured_pieces, game.player2.captured_pieces), ":",
    #       min(game.player1.captured_pieces, game.player2.captured_pieces))


if __name__ == '__main__':
    make_n_games(100, "no_danger", "random")
