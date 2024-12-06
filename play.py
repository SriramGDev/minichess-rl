from itertools import permutations

# Runs a match with the given game and list of players.
# Returns a dictionary of points. It will map each player object to its score.
# For each match, a player gains a point if it wins, loses a point if it loses,
# and gains no points if it ties.
def play_match(game, players, verbose=False, permute=False):

    # You can use permutations to break the dependence on player order in measuring strength.
    matches = list(permutations(players)) if permute else [players]
    
    # Initialize scoreboard
    scores = {}
    for p in players:
        scores[p] = 0
        p.reset() # Reset incoming players as a precaution.

    # Run the matches (there will be multiple if permute=True)
    for m in matches:
        s, state_map = game.get_initial_state()
        if verbose: game.visualize(s)
        winner = game.check_winner(s, state_map)
        while winner is None:
            p_num = game.get_player(s)
            p = m[p_num]
            if verbose: print("Player {}'s turn.".format(p_num))
            s, state_map = p.update_state(s, state_map)
            if verbose: game.visualize(s)
            winner = game.check_winner(s, state_map)
        for i, p in enumerate(m):
            if winner == -1:
                scores[p] += .5/len(matches)
            elif winner == i:
                scores[p] += 1/len(matches)
            p.reset() # Clear our tree to make the next match fair

    # Assign an outcome to each player (Win, Lose, or Tie)
    outcomes = {}
    num_players = game.get_num_players()
    for p in scores:
        if scores[p] < 1/num_players:
            outcomes[p] = "Lose"
        elif scores[p] == 1/num_players:
            outcomes[p] = "Tie"
        else:
            outcomes[p] = "Win"

    return scores, outcomes



if __name__ == "__main__":
    from players.human_player import HumanPlayer
    from players.human_minichess_player import HumanMinichessPlayer
    from neural_network import NeuralNetwork
    from models.zero import Zero
    from players.uninformed_mcts_player import UninformedMCTSPlayer
    from players.deep_mcts_player import DeepMCTSPlayer
    from games.minichess import MiniChess


    # Change these variable 
    game = MiniChess()
    ckpt = 140
    nn = NeuralNetwork(game, Zero, cuda=False)
    nn.load(ckpt)
    
    human =  HumanMinichessPlayer(game)
    uninformed = UninformedMCTSPlayer(game, simulations=640)
    deep = DeepMCTSPlayer(game, nn, simulations=200)
    
    players = [deep, human]
    for _ in range(1):
        print(play_match(game, players, verbose=True, permute=True))
    
