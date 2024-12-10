from itertools import permutations
import argparse
import sys
import os
from utils.colors import Colors, Styles
import getpass
from itertools import cycle
from threading import Thread, Event
from time import sleep

def play_match(level, black):
    from players.human_minichess_player import HumanMinichessPlayer
    from neural_network import NeuralNetwork
    from models.zero import Zero
    from players.deep_mcts_player import DeepMCTSPlayer
    from games.minichess import MiniChess

    try:
        game = MiniChess()
        ckpt = 320
        nn = NeuralNetwork(game, Zero, cuda=False)
        nn.load(ckpt)

        human =  HumanMinichessPlayer(game)
        deep = DeepMCTSPlayer(game, nn, simulations=args.level*10)
        deep1 = DeepMCTSPlayer(game, nn, simulations=args.level*10)
        if black:
            players = [deep, human]
            human_num = 1
        else:
            players = [deep1, deep]
            human_num = 0

        s, state_map = game.get_initial_state()
        winner = game.check_winner(s, state_map)
        while winner is None:
            p_num = game.get_player(s)
            p = players[p_num]

            rows = game.visualize(s, flip=black).split("\n")
            white_token = " "
            black_token = " "
            if p_num == 0:
                white_token = "\u25c9"
            else:
                black_token = "\u25c9"

            rows[0] += "{}{}{} {}{}MiniChess-Zero (Lvl. {}){}".format(Styles.PADDING_SMALL, Colors.GREEN, white_token if black else black_token, Colors.BOLD, Colors.LIGHT, level, Colors.RESET)
            rows[-3] += "{}{}{} {}{}{}{}".format(Styles.PADDING_SMALL, Colors.GREEN, black_token if black else white_token , Colors.BOLD, Colors.LIGHT, getpass.getuser(), Colors.RESET)
            os.system('clear')
            print("\n\n\n\n")
            print("\n".join(rows))

            s, state_map = p.update_state(s, state_map)

            winner = game.check_winner(s, state_map)

        rows = game.visualize(s, flip=black).split("\n")
        rows[0] += "{}{}\u25c9 {}{}MiniChess-Zero (Lvl. {}){}".format(Styles.PADDING_SMALL, Colors.GREEN, Colors.BOLD, Colors.LIGHT, level, Colors.RESET)
        rows[-3] += "{}{}\u25c9 {}{}{}{}".format(Styles.PADDING_SMALL, Colors.GREEN, Colors.BOLD, Colors.LIGHT, getpass.getuser(), Colors.RESET)
        if winner == 0:
            rows[-5] += "{}{}{}{} White wins {}".format(Styles.PADDING_MEDIUM, Colors.DARK, Colors.Backgrounds.WHITE, Colors.BOLD, Colors.RESET)

        elif winner == 1:
            rows[-5] += "{}{}{}{} Black wins {}".format(Styles.PADDING_MEDIUM, Colors.LIGHT, Colors.Backgrounds.BLACK, Colors.BOLD, Colors.RESET)

        else:
            rows[-5] += "{}{}{}{} Draw {}".format(Styles.PADDING_MEDIUM, Colors.LIGHT, Colors.Backgrounds.PURPLE_LIGHT, Colors.BOLD, Colors.RESET)

        os.system('clear')
        print("\n\n\n\n")
        print("\n".join(rows))

    except KeyboardInterrupt:
        if black:
            winner = 0
        else:
            winner = 1

        rows = game.visualize(s, flip=black).split("\n")
        rows[0] += "{}{}\u25c9 {}{}MiniChess-Zero (Lvl. {}){}".format(Styles.PADDING_SMALL, Colors.GREEN, Colors.BOLD, Colors.LIGHT, level, Colors.RESET)
        rows[-3] += "{}{}\u25c9 {}{}{}{}".format(Styles.PADDING_SMALL, Colors.GREEN, Colors.BOLD, Colors.LIGHT, getpass.getuser(), Colors.RESET)
        if winner == 0:
            rows[-5] += "{}{}{}{} White wins {}{}{}(by resignation){}".format(Styles.PADDING_MEDIUM, Colors.DARK, Colors.Backgrounds.WHITE, Colors.BOLD, Colors.RESET, Colors.BOLD, Colors.ORANGE, Colors.RESET)

        elif winner == 1:
            rows[-5] += "{}{}{}{} Black wins {}{}{}(by resignation){}".format(Styles.PADDING_MEDIUM, Colors.LIGHT, Colors.Backgrounds.BLACK, Colors.BOLD, Colors.RESET, Colors.BOLD, Colors.ORANGE, Colors.RESET)

        os.system('clear')
        print("\n\n\n\n")
        print("\n".join(rows))


if __name__ == "__main__":
    import warnings
    warnings.filterwarnings("ignore")
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--level", help="strength of AI opponent", type=int, default=5)
    parser.add_argument("-p", "--play-as", help="color to play as", type=str, default="white")
    args = parser.parse_args()
    
    play_match(level=args.level, black=(args.play_as=="black"))
    
