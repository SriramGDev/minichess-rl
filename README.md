# Reinforcement Learning for Gardner Minichess

This project is an adaptation of a general-purpose AlphaZero implementation from [petosa/simple-alpha-zero](https://github.com/petosa/simple-alpha-zero).

It has a user-friendly TUI and comes with a trained agent which can be played against.

## Playing MiniChess

A Minichess model has been trained on 162000 games of self-play. You can play against this model by running `python minichs.py`. 

You can play against the model at strength `N` by adding the `--level {N}` flag.

You can choose which color you play as by adding the `--play-as {color}` flag, where `{color}` is one of `white` or `black`.

By default, (i.e., no flags), you will play as white against an agent of strength `5`.

## Training a Minichess agent

The parameters used to train the Minichess agent can be found in `configs/minichess-cpu.json` To train your own Minichess agent, copy this file and change the parameters to your liking, then run:

`python main.py configs/my_run_configuration.json`

If you wish to continue training the existing Minichess agent, you can do so by simply running:

`python main.py configs/minichess-cpu.json`

