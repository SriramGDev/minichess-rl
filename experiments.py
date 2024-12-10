import os
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
from neural_network import NeuralNetwork
from players.deep_mcts_player import DeepMCTSPlayer
from players.deep_mcts_player import DeepMCTSPlayerAction
from players.uninformed_mcts_player import UninformedMCTSPlayer
from play import play_match

from models.zero import Zero
from games.minichess import MiniChess


# Evaluate the outcome of playing a checkpoint against an uninformed MCTS agent
def evaluate_against_uninformed(checkpoint, game, model_class, my_sims, opponent_sims, cuda=False):
    my_model = NeuralNetwork(game, model_class, cuda=cuda)
    my_model.load(checkpoint)
    num_opponents = game.get_num_players() - 1
    uninformeds = [UninformedMCTSPlayer(game, opponent_sims) for _ in range(num_opponents)]
    informed = DeepMCTSPlayer(game, my_model, my_sims)
    scores, outcomes = play_match(game, [informed] + uninformeds, permute=True)
    score, outcome = scores[informed], outcomes[informed]
    print("Opponent strength: {}     My win rate: {} ({})".format(opponent_sims, round(score, 3), outcome))


# Tracks the current best checkpoint across all checkpoints
def rank_checkpoints(game, model_class, sims, cuda=False):
    winning_model = NeuralNetwork(game, model_class, cuda=cuda)
    contending_model = NeuralNetwork(game, model_class, cuda=cuda)
    ckpts = winning_model.list_checkpoints()
    num_opponents = game.get_num_players() - 1
    current_winner = ckpts[0]

    for contender in ckpts:

        # Load contending player
        contending_model.load(contender)
        contending_player = DeepMCTSPlayer(game, contending_model, sims)

        # Load winning player
        winning_model.load(current_winner)
        winners = [DeepMCTSPlayer(game, winning_model, sims) for _ in range(num_opponents)]
        
        scores, outcomes = play_match(game, [contending_player] + winners, verbose=False, permute=True)
        score, outcome = scores[contending_player], outcomes[contending_player]
        print("Current Champ: {}    Challenger: {}    Outcome: {} <{}>    "
                .format(current_winner, contender, outcome, score), end= "")
        if outcome == "Win":
            current_winner = contender
        print("New Champ: {}".format(current_winner))


# Plays the given checkpoint against all other checkpoints and logs upsets.
def one_vs_all(checkpoint, game, model_class, sims, cuda=False):
    my_model = NeuralNetwork(game, model_class, cuda=cuda)
    my_model.load(checkpoint)
    contending_model = NeuralNetwork(game, model_class, cuda=cuda)
    ckpts = my_model.list_checkpoints()
    num_opponents = game.get_num_players() - 1

    for contender in ckpts:
        contending_model.load(contender)
        my_player = DeepMCTSPlayer(game, my_model, sims)
        contenders = [DeepMCTSPlayer(game, contending_model, sims) for _ in range(num_opponents)]
        scores, outcomes = play_match(game, [my_player] + contenders, verbose=False, permute=True)
        score, outcome = scores[my_player], outcomes[my_player]
        print("Challenger:", contender, "Outcome:", outcome, score)


# Finds the effective MCTS strength of a checkpoint
# Also presents a control at each checkpoint - that is, the result
# if you had used no heuristic but the same num_simulations.
def effective_model_power(checkpoint, game, model_class, sims, cuda=False):
    my_model = NeuralNetwork(game, model_class, cuda=cuda)
    my_model.load(checkpoint)
    my_player = DeepMCTSPlayer(game, my_model, sims)
    strength = 10
    num_opponents = game.get_num_players() - 1
    lost = False

    while not lost: 
        contenders = [UninformedMCTSPlayer(game, strength) for _ in range(num_opponents)]

        # Play main game
        scores, outcomes = play_match(game, [my_player] + contenders, verbose=False, permute=True)
        score, outcome = scores[my_player], outcomes[my_player]
        if outcome == "Lose": lost = True
        print("{} <{}>      Opponent strength: {}".format(outcome, round(score, 3), strength), end="")

        # Play control game
        control_player = UninformedMCTSPlayer(game, sims)
        scores, outcomes = play_match(game, [control_player] + contenders, verbose=False, permute=True)
        score, outcome = scores[control_player], outcomes[control_player]
        print("      (Control: {} <{}>)".format(outcome, round(score, 3)))

        strength *= 2 # Opponent strength doubles every turn


def plot_train_loss(game, model_classes, cudas):
    fig, ax = plt.subplots()
    min_len = None
    for cuda, model_class in zip(cudas, model_classes):
        nn = NeuralNetwork(game, model_class, cuda=cuda)
        ckpt = nn.list_checkpoints()[-1]
        _, error = nn.load(ckpt, load_supplementary_data=True)
        window = 1
        error = np.convolve(error, np.ones(window), mode="valid")/window
        min_len = len(error) if min_len is None else min(min_len, len(error))
        plt.plot(error, label=model_class.__name__)
        

    plt.title("Training loss for CNN")
    ax.set_xlim(left=0, right=min_len)
    ax.set_ylabel("Error")
    ax.set_xlabel("Iteration")
    plt.savefig("../../../report/images/loss.png", dpi=400)
    plt.hist(error, bins=50)
    plt.show()

def openings(game, model_class, cuda, a):
    nn = NeuralNetwork(game, model_class, cuda=cuda)
    checkpoints = nn.list_checkpoints()
    a = (5-int(a[1]), ord(a[0])-ord('a'), 5-int(a[3]), ord(a[2])-ord('a'))
    s, state_map = game.get_initial_state()
    available = game.get_available_actions(s)
    template = np.zeros_like(available)
    template[a] = 1
    new_s, new_state_map = game.take_action(s, state_map, template)
    responses = defaultdict(int)
    for ckpt in checkpoints:
        nn.load(ckpt)
        deep = DeepMCTSPlayerAction(game, nn, simulations=50)
        action = deep.update_state(new_s, new_state_map)
        responses[action] += 1
    return responses

def strength(checkpoint, game, model_class, sims, cuda=False, num_games=50):
    my_model = NeuralNetwork(game, model_class, cuda=cuda)
    my_model.load(checkpoint)
    my_player = DeepMCTSPlayer(game, my_model, sims)
    contender = UninformedMCTSPlayer(game, sims)
    scores = []
    for _ in tqdm(range(num_games)):
        score, outcomes = play_match(game, [my_player, contender], verbose=False, permute=True)
        scores.append(score[my_player])
    return scores

if __name__ == "__main__":
    checkpoint = 13
    game = MiniChess()
    model_class = Zero
    sims = 50
    cuda = False
    
    #print("*** Rank Checkpoints ***")
    #rank_checkpoints(game, model_class, sims, cuda)
    #print("*** One vs All ***")
    #one_vs_all(checkpoint, game, model_class, sims, cuda)
    #print("*** Effective Model Power ***")
    #effective_model_power(checkpoint, game, model_class, sims, cuda)
    #plot_train_loss(game, [model_class], [cuda])
    #for file in ["a", "b", "c", "d", "e"]:
    #    move = "{}2{}3".format(file, file)
    #    print(dict(openings(game, model_class, cuda, move)))

    ckpt_score = []
    for ckpt in range(10, 360, 10):
        scores = strength(ckpt, game, model_class, 10, num_games=10)
        ckpt_score.append(sum(scores))


    fig, ax = plt.subplots(1)
    ax.set_title("Performance vs. uninformed MCTS")
    ax.set_xlabel("Checkpoint")
    ax.set_ylabel("Games won")
    ax.plot(list(range(10,360,10)), ckpt_score)
    plt.savefig("../../../report/images/uninformed.png", dpi=400)
    plt.show()


    '''
    x = [10,20,40,80,160,320,640,1280,2560,5120,10240,20480]
    control = [1., .5, .5, .25, .25, .25, .25, .25, .25, .25, .5, .5]
    senet = [1., .75, .75, .75, .75, .75, .75, .5, .5, .5, .5, .5]
    mini = [1., .75, .75, .75, .75, .75, .75, .5, .5, .5, .5, .5]
    mlp = [1., .5, .5, .5, .5, .5, .5, .5, .5, .5, .5, .5]
    print("control", sum(control)/len(control))
    print("senet", sum(senet)/len(senet))
    print("mini", sum(mini)/len(mini))
    print("mlp", sum(mlp)/len(mlp))

    f, ax = plt.subplots()
    plt.plot(x, control, color="black", label="Vanilla (Control)", linewidth=4)
    plt.plot(x,senet, label="SENet", linewidth=4)
    plt.plot(x,mini, linestyle="--", label="MiniVGG", linewidth=4)
    plt.plot(x,mlp, linestyle=":", label="MLP", linewidth=4)
    plt.ylabel("AlphaZero Win Rate")
    plt.xscale("log")
    plt.xlabel("Opponent Vanilla MCTS Iterations per Turn (Opponent Strength)")
    plt.legend()
    ax.set_ylim(ymin=0)
    plt.title("TicTacToe - AlphaZero vs Vanilla MCTS Opponents")
    plt.show()

    '''

    '''
    x = [10,20,40,80,160,320,640,1280,2560,5120,10240,20480]
    control = [1.0, .75, .25, 1.0, .25, 0, .25, 0, 0, 0, 0, 0]
    senet = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0,.75, .5, 0]
    small = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,.5,0,0,.5,1]
    mlp = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,.25,.5,0,.5]

    print("control", sum(control)/len(control))
    print("senet", sum(senet)/len(senet))
    print("small", sum(small)/len(small))
    print("mlp", sum(mlp)/len(mlp))
    f, ax = plt.subplots()
    plt.plot(x, control, color="black", label="Vanilla (Control)", linewidth=4)
    plt.plot(x,senet, label="SENet", linewidth=4)
    plt.plot(x,small, linestyle="--", label="SmallVGG", linewidth=4)
    plt.plot(x,mlp, linestyle=":", label="MLP", linewidth=4)
    plt.ylabel("AlphaZero Win Rate")
    plt.xscale("log")
    plt.xlabel("Opponent Vanilla MCTS Iterations per Turn (Opponent Strength)")
    plt.legend()
    ax.set_ylim(ymin=0)
    plt.title("Connect4 - AlphaZero vs Vanilla MCTS Opponents")
    plt.show()
    '''
