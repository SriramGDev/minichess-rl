import sys
import numpy as np
sys.path.append("..")
from mcts import MCTS
from player import Player

class DeepMCTSPlayer(Player):

    def __init__(self, game, nn, simulations):
        self.game = game
        self.simulations = simulations
        self.nn = nn
        self.tree = MCTS(game, nn)

    def update_state(self, s, state_map):
        print("")
        for _ in range(self.simulations):
            self.tree.simulate(s, state_map)

        dist = self.tree.get_distribution(s, 0)
        a = tuple(dist[np.argmax(dist[:,1]),0])
        available = self.game.get_available_actions(s)
        template = np.zeros_like(available)
        template[a] = 1
        s_prime, state_map_prime = self.game.take_action(s, state_map, template)
        return s_prime, state_map_prime

    def reset(self):
        self.tree = MCTS(self.game, self.nn)
