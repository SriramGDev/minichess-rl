import numpy as np
import os
import math
import sys
sys.path.append("..")
from game import Game
from collections import defaultdict
from utils.colors import Colors, Styles

layer_map = { 0: "P", 1: "R", 2: "N", 3: "B", 4: "Q", 5: "K", 6: "P", 7: "R",
        8: "N", 9: "B", 10: "Q", 11: "K"}

unicode_rep = {"P": '\u265f', "R": '\u265c', "N": '\u265e', "B": '\u265d', "Q":
        '\u265b', "K": '\u265a', "k": Colors.DARK+'\u265a', "q": Colors.DARK+'\u265b', "r": Colors.DARK+'\u265c',
        "b": Colors.DARK+'\u265d', "n": Colors.DARK+'\u265e', "p": Colors.DARK+'\u265f', " ": " "}

class MiniChess(Game):
    # Returns an ndarray representing the initial game state.
    # Note that array values should be between 0 and 1.
    def get_initial_state(self):
        state_map = defaultdict(int)
        board = np.zeros((12+1, 5, 5), dtype=np.float32) # 5 x 5 board, one layer for each white piece, one for each black piece, one for current player
        for (layer, row) in [(0, 3), (6, 1)]: # place pawns
            board[layer, row, :] = 1
        for col in range(5):
            for player in range(2):
                board[player*6+col+1, (1-player)*4, col] = 1
        state_map[board.tostring] += 1
        return board, state_map

    def is_square(self, i, j):
        return (i >= 0 and i < 5 and j >= 0 and j < 5)

    # Returns a boolean ndarray of actions, where True indicates an available action
    # and False indicates an unavailable action at the current state s.
    # The shape of this action ndarray does not have to match the shape of the state.
    def get_available_actions(self, s):
        actions = np.zeros((5, 5, 5, 5), dtype=bool) # actions[i][j][k][l] represents whether the piece at position (i,j) can move to (k,l)
        white_pieces = s[:6, :, :].sum(axis=0)
        black_pieces = s[6:12, :, :].sum(axis=0)
        is_empty = ((white_pieces+black_pieces) == 0) # mask empty squares
        current_color = int(s[12, 0, 0])
        if current_color == 0:
            my_color = white_pieces
        else:
            my_color = black_pieces
        for i in range(5):
            for j in range(5):
                if current_color == 1 and s[5,i,j] == 1.:
                    king_position = (i,j)
                elif current_color == 0 and s[11,i,j] == 1.:
                    king_position = (i,j)
        for i in range(5):
            for j in range(5):
                for layer in range(current_color*6, current_color*6+6):
                    if s[layer, i, j] == 1.:
                        if layer_map[layer] == "P":
                            if current_color == 1:
                                if self.is_square(i+1, j) and is_empty[i+1, j]: # square in front of black pawn is empty
                                    actions[i, j, i+1, j] = True
                                if self.is_square(i+1, j-1) and white_pieces[i+1, j-1] != 0: # square to front right of black pawn has a white piece that can be captured
                                    actions[i, j, i+1, j-1] = True
                                if self.is_square(i+1, j+1) and white_pieces[i+1, j+1] != 0: # square to front left of black pawn has a white piece that can be captured
                                    actions[i, j, i+1, j+1] = True

                            elif current_color == 0:
                                if self.is_square(i-1, j) and is_empty[i-1, j]: # square in front of white pawn is empty
                                    actions[i, j, i-1, j] = True
                                if self.is_square(i-1, j-1) and black_pieces[i-1, j-1] != 0: # square to front right of white pawn has a black piece that can be captured
                                    actions[i, j, i-1, j-1] = True
                                if self.is_square(i-1, j+1) and black_pieces[i-1, j+1] != 0: # square to front left of white pawn has a black piece that can be captured
                                    actions[i, j, i-1, j+1] = True

                        elif layer_map[layer] == "R":
                            actions = self.rook_actions(i, j, is_empty, my_color, actions)

                        elif layer_map[layer] == "N":
                            actions = self.knight_actions(i, j, my_color, actions)

                        elif layer_map[layer] == "B":
                            actions = self.bishop_actions(i, j, is_empty, my_color, actions)

                        elif layer_map[layer] == "Q":
                            actions = self.rook_actions(i, j, is_empty, my_color, actions)
                            actions = self.bishop_actions(i, j, is_empty, my_color, actions)

                        elif layer_map[layer] == "K":
                            actions = self.king_actions(i, j, is_empty, my_color, actions)

        for i in range(5):
            for j in range(5):
                if actions[i,j,king_position[0],king_position[1]]:
                    actions = np.zeros((5,5,5,5), dtype=bool)
                    actions[i,j,king_position[0],king_position[1]] = True # force king capture if possible
        return actions

    def rook_actions(self, i, j, is_empty, my_color, actions):
        forward, left, back, right = 1, 1, 1, 1
        while self.is_square(i-forward, j) and is_empty[i-forward, j]:
            actions[i, j, i-forward, j] = True
            forward += 1
        if self.is_square(i-forward, j) and my_color[i-forward, j] == 0.: # rook can capture
            actions[i, j, i-forward, j] = True

        while self.is_square(i+back, j) and is_empty[i+back, j]:
            actions[i, j, i+back, j] = True
            back += 1
        if self.is_square(i+back, j) and my_color[i+back, j] == 0.: # rook can capture
            actions[i, j, i+back, j] = True

        while self.is_square(i, j-left) and is_empty[i, j-left]:
            actions[i, j, i, j-left] = True
            left += 1
        if self.is_square(i, j-left) and my_color[i, j-left] == 0.: # rook can capture
            actions[i, j, i, j-left] = True

        while self.is_square(i, j+right) and is_empty[i, j+right]:
            actions[i, j, i, j+right] = True
            right += 1
        if self.is_square(i, j+right) and my_color[i, j+right] == 0.: # rook can capture
            actions[i, j, i, j+right] = True

        return actions

    def knight_actions(self, i, j, my_color, actions):
        knight_moves = zip([-2, -2, -1, -1, 1, 1, 2, 2], [-1, 1, -2, 2, -2, 2, -1, 1])
        for (di, dj) in knight_moves:
            new_i = i+di
            new_j = j+dj
            if self.is_square(new_i, new_j):
                if my_color[new_i, new_j] == 0.: # no black piece, so knight can move, possibly capturing
                    actions[i, j, new_i, new_j] = True
        return actions


    def bishop_actions(self, i, j, is_empty, my_color, actions):
        dist = 1
        # Check up and left
        while self.is_square(i-dist, j-dist) and is_empty[i-dist, j-dist]:
            actions[i, j, i-dist, j-dist] = True
            dist += 1
        if self.is_square(i-dist, j-dist) and my_color[i-dist, j-dist] == 0.:
            actions[i, j, i-dist, j-dist] = True

        dist = 1
        # Check up and right 
        while self.is_square(i-dist, j+dist) and is_empty[i-dist, j+dist]:
            actions[i, j, i-dist, j+dist] = True
            dist += 1
        if self.is_square(i-dist, j+dist) and my_color[i-dist, j+dist] == 0.:
            actions[i, j, i-dist, j+dist] = True

        dist = 1
        # Check down and left
        while self.is_square(i+dist, j-dist) and is_empty[i+dist, j-dist]:
            actions[i, j, i+dist, j-dist] = True
            dist += 1
        if self.is_square(i+dist, j-dist) and my_color[i+dist, j-dist] == 0.:
            actions[i, j, i+dist, j-dist] = True

        dist = 1
        # Check down and right 
        while self.is_square(i+dist, j+dist) and is_empty[i+dist, j+dist]:
            actions[i, j, i+dist, j+dist] = True
            dist += 1
        if self.is_square(i+dist, j+dist) and my_color[i+dist, j+dist] == 0.:
            actions[i, j, i+dist, j+dist] = True

        return actions

    def king_actions(self, i, j, is_empty, my_color, actions):
        king_moves = zip([-1, -1, -1, 0, 0, 1, 1, 1], [-1, 0, 1, -1, 1, -1, 0, 1])
        for (di, dj) in king_moves:
            new_i = i+di
            new_j = j+dj
            if self.is_square(new_i, new_j):
                if my_color[new_i, new_j] == 0.:
                    actions[i, j, new_i, new_j] = True
        return actions


    # Given the current state, evaluate if the game has ended.
    # Convention:
    # Return None if there is no winner yet.
    # Return -1 if there is a tie.
    # Otherwise return the player number that won.
    def check_winner(self, s, state_map):
        if state_map[s.tostring()] >= 3: # threefold repetition -> draw
            return -1
        current_color = int(s[12, 0, 0])
        has_king = False
        # check if we have a king
        for i in range(5):
            for j in range(5):
                if s[current_color*6+5, i, j] == 1.:
                    has_king = True
        if not has_king: # our king has been captured, so we lose
            return 1-current_color
        
        if not self.get_available_actions(s).any(): # we cannot move, but our king is still on the board
            return -1
    
        return None

    def get_action_tuple(self, a):
        for i in range(5):
            for j in range(5):
                for k in range(5):
                    for l in range(5):
                        if a[i,j,k,l]:
                            return (i,j,k,l)

    # Given a state s and action a, produces a new ndarray s' which is the
    # resulting state from taking action a in state s.
    # Note that array values should be between 0 and 1.
    # Make sure this does NOT modify s in-place; return a new ndarray instead.
    def take_action(self, s, state_map, a):
        a = self.get_action_tuple(a)
        current_color = int(s[12, 0, 0])
        new_s = s.copy()
        piece_layer = -1
        for layer in range(current_color*6, current_color*6+6):
            if s[layer, a[0], a[1]] == 1.:
                piece_layer = layer
                break
        if layer_map[piece_layer] == "P" and (a[2] == 0 or a[2] == 4): # pawn promotion
            new_s[piece_layer, a[0], a[1]] = 0.
            new_s[current_color*6+4, a[2], a[3]] = 1.
        else:
            new_s[piece_layer, a[2], a[3]] = 1.
            new_s[piece_layer, a[0], a[1]] = 0.
        # process capture, if it occurred
        for layer2 in range((1-current_color)*6, (1-current_color)*6+6):
            if new_s[layer2, a[2], a[3]] == 1.:
                new_s[layer2, a[2], a[3]] = 0.   
        new_s[12, :, :] = (1.-new_s[12, :, :]) # switch players
        new_state_map = state_map.copy()
        new_state_map[new_s.tostring()] += 1
        return new_s, new_state_map

    # Given the current state s, return an integer indicating which player's turn it is.
    # The first player is 0, second player is 1, and so on.
    def get_player(self, s):
        return int(s[12, 0, 0])

    # Return the number of players in this game.
    def get_num_players(self):
        return 2

    # Visualizes the given state.
    def visualize(self, s, flip=False):
        vis_s = [[" " for _ in range(5)] for _ in range(5)]
        for layer in range(12):
            for i in range(5):
                for j in range(5):
                    if s[layer, i, j] == 1.:
                        vis_s[i][j] = layer_map[layer]
                        if layer >= 6:
                            vis_s[i][j] = vis_s[i][j].lower()
        if flip:
            for t in vis_s: t.reverse()
            vis_s.reverse()
        out = ""
        for i in range(5):
            row = ""
            for j in range(5):
                if (i+j)%2 == 0:
                    row += Colors.Backgrounds.DARK+unicode_rep[vis_s[i][j]]+" "+Colors.RESET
                else:
                    row += Colors.Backgrounds.LIGHT+unicode_rep[vis_s[i][j]]+" "+Colors.RESET
            if flip:
                out += "{}{}{}{} {}\n".format(Styles.PADDING_MEDIUM, Colors.GRAY, str(i+1), Colors.RESET, row)
            else:
                out += "{}{}{}{} {}\n".format(Styles.PADDING_MEDIUM, Colors.GRAY, str(5-i), Colors.RESET, row)
        if flip:
            out += "{}{}  e d c b a\n".format(Styles.PADDING_MEDIUM, Colors.GRAY, Colors.RESET)
        else:
            out += "{}{}  a b c d e\n".format(Styles.PADDING_MEDIUM, Colors.GRAY, Colors.RESET)

        return out
