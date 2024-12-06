import sys
import numpy as np
sys.path.append("..")
from player import Player
from utils.colors import Colors, Styles

class HumanMinichessPlayer(Player):

    def __init__(self, game):
        self.game = game

    def update_state(self, s, state_map):
        while True:
            try:
                a = input('{}{}{}┏━ Your move ━━━━━━━━━━━┓ \n{}┗{}{}'.format(
                    Styles.PADDING_SMALL, Colors.WHITE, Colors.BOLD,\
                            Styles.PADDING_SMALL, Styles.PADDING_SMALL,
                            Colors.RESET))
                a = (5-int(a[1]), ord(a[0])-ord('a'), 5-int(a[3]), ord(a[2])-ord('a'))
                available = self.game.get_available_actions(s)
                template = np.zeros_like(available)
                template[a] = 1
                if available[template] == 1:
                    break
            except (ValueError, IndexError):
                pass
            print("Invalid move! Try again.")
        s_prime, state_map_prime = self.game.take_action(s, state_map, template)
        return s_prime, state_map_prime

    def reset(self):
        pass
