# Gambit

## Project Information
This is the README file for Gambit, software tools for game theory. The latest information on Gambit can be obtained from the Gambit website at http://www.gambit-project.org

## Installation Instructions
Instructions on installing Gambit can be found in the PERSONAL_INSTALL file in this directory.

## How to Use:
You'll need to change the directory to:
```
src/python/gambit/tests/test_games/personal_test_games
```

### Configurations
If you'd like to change the default configuration. Open the `config.ini` file.

### Run the program.
To run the program open the command and input:
```
python gen_tree_manila_poker.py
```

### How the Program Works
**Step 1: Create the Saver Object**
The saver object is an object that holds all the information given in the `config.ini` file pertaining to writing to files. Therefore, it's needed to print the games (their original and reduced forms) and their solutions.

**Step 2: Create the Poker Game Object**
Every other bit of information not stored in the Saver object is stored in the Poker game object. This is also where we verify that any information given pertaining to the game is inspected to ensure we don't get errors deep in the code.

**Step 3: Create the Game Tree**
Here we create the Game tree following the (potentially restriced)
rules of Texas Hold'Em Poker.  This game is printed to `OUTPUTS_DIRECTORY/OUTPUT_DIRECTORY/ORIGINAL_GAME_TREE_FILE` in .nfg and .gte format.

**Step 4: Prune the Game Tree**
Here, we remove actions that lead to player giving himself a strictly worse payoff. This game is printed to `OUTPUTS_DIRECTORY/OUTPUT_DIRECTORY/PRINT_PRUNED_GAME_TREE` in .nfg and .gte format.

**Step 5: Convert the Game to Matrix of Undominated Strategies**
This is not verified as working, at the moment. Moreover, we're not sure it's what we want. This game is printed to `OUTPUTS_DIRECTORY/OUTPUT_DIRECTORY/UNDOMINATED_GAME_MATRIX_FILE` in .nfg and .gte format.

**Step 6: Solve the Game**
With a throughly reduced game, the game can be solve for pure/mixed strategies. For more information on this, see the "Some Gambit Information" section. These solutions are printed to `OUTPUTS_DIRECTORY/OUTPUT_DIRECTORY/SOLUTIONS_FILE`. We're working on cleaning up these solutions to give a user-friendly and readable solutions file.

### Some Gambit Information

**How do we prune the tree of strictly dominated strategies?**
First, we gather all information sets we'd like to possibly remove actions from. Then, for each information set, we gather all contingencies (all possible events) that reach this information set. Then, we get the outcomes of all these contingencies and compute the expected payoff for a player who owns the information set for each action they can take. We then remove the actions that are strictly dominated.

**How do we solve the game?**
Gambit handles this in the backend when we call:

```python
# create solver
solver = gambit.nash.ExternalEnumMixedSolver()

# solve game
solutions = solver.solve(g)
```

What this does is it converts the game tree to matrix-form by gathering all contingencies (all possible events) by calling `g.tree.contingencies` and setting the payoffs to be the payoffs given those contingencies occurred. 
