import gambit, math, time, os, sys
from utils import compute_time_of
from fractions import Fraction
from numbers import Rational

def create_tree(args):

    # create tree and add some information
    g = gambit.Game.new_tree()
    g.title = TITLE
    g.players.add(PLAYER_1)
    g.players.add(PLAYER_2)

    # Chance node
    iset = g.root.append_move(g.players.chance, 2)
    iset.actions[0].label = "A"
    iset.actions[1].label = "QK"

    # Rose's moves
    iset = g.root.children[0].append_move(g.players[PLAYER_1], 2)
    iset.label = "{} has A".format(PLAYER_1)
    iset.actions[0].label = "Bet 1"
    iset.actions[1].label = "Bet 3"

    iset = g.root.children[1].append_move(g.players[PLAYER_1], 2)
    iset.label = "{} has QK".format(PLAYER_1)
    iset.actions[0].label = "Bet 1"
    iset.actions[1].label = "Bet 3"

    # Colin's moves
    iset = g.root.children[0].children[0].append_move(g.players[PLAYER_2], 2)
    iset.label = "{} has A and {}".format(PLAYER_1, "Bet 1")
    iset.actions[0].label = "Yes"
    iset.actions[1].label = "No"

    iset = g.root.children[0].children[1].append_move(g.players[PLAYER_2], 2)
    iset.label = "{} has A and {}".format(PLAYER_1, "Bet 3")
    iset.actions[0].label = "Yes"
    iset.actions[1].label = "No"

    iset = g.root.children[1].children[0].append_move(g.players[PLAYER_2], 2)
    iset.label = "{} has QK and {}".format(PLAYER_1, "Bet 1")
    iset.actions[0].label = "Yes"
    iset.actions[1].label = "No"

    iset = g.root.children[1].children[1].append_move(g.players[PLAYER_2], 2)
    iset.label = "{} has QK and {}".format(PLAYER_1, "Bet 3")
    iset.actions[0].label = "Yes"
    iset.actions[1].label = "No"

    # Specify outcomes
    default_outcome = g.outcomes.add("Default outcome")
    default_outcome[0] = 1
    default_outcome[1] = -1

    g.root.children[0].children[0].children[0].outcome = multiply_outcome(g, default_outcome, 1)
    g.root.children[0].children[0].children[1].outcome = multiply_outcome(g, default_outcome, 2)
    g.root.children[0].children[1].children[0].outcome = multiply_outcome(g, default_outcome, 3)
    g.root.children[0].children[1].children[1].outcome = multiply_outcome(g, default_outcome, 6)

    g.root.children[1].children[0].children[0].outcome = multiply_outcome(g, default_outcome, 1)
    g.root.children[1].children[0].children[1].outcome = multiply_outcome(g, default_outcome,-2)
    g.root.children[1].children[1].children[0].outcome = multiply_outcome(g, default_outcome, 3)
    g.root.children[1].children[1].children[1].outcome = multiply_outcome(g, default_outcome,-6)

    return g

def multiply_outcome(g, outcome, multiple):
    new_outcome = g.outcomes.add("Default outcome multiplied by {}".format(multiple))
    new_outcome[0] =  multiple
    new_outcome[1] = -multiple
    return new_outcome

'''
Solve the game.
'''
def solve_game(args):

    # create solver
    solver = gambit.nash.ExternalEnumMixedSolver()
    
    # solve game
    solutions = solver.solve(g)
    return solutions

'''
Create a solutions directory and save the solutions there.
'''
def print_solutions(args):
    
    # create directory and cd in
    os.mkdir(SOLUTIONS_DIRECTORY)
    os.chdir(SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP.nfg".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    for solution in solutions:
        target_file.write("{}\n".format(str(solution)))
    
    # go back out
    os.chdir(PARENT_DIRECTORY)

if __name__ == '__main__':

    # directory names
    PARENT_DIRECTORY = ".."
    SAVED_GAMES_DIRECTORY = "saved"
    SOLUTIONS_DIRECTORY = "Solutions-for-PSP-Games-{}".format(time.strftime("%Y-%m-%d %H:%M:%S"))

    # get file name
    if len(sys.argv) != 4:
        print("ERROR: Please supply: a title, a name for player 1, a name for player 2")
        sys.exit(2)
    else:
        TITLE = sys.argv[1]
        PLAYER_1 = sys.argv[2]
        PLAYER_2 = sys.argv[3]


    # create the tree
    g = compute_time_of(1, "Creating Tree", create_tree)

    # solve the game
    solutions = compute_time_of(2, "Solving Game", solve_game)

    # print the solutions to a file
    compute_time_of(3, "Printing Solutions", print_solutions)  
