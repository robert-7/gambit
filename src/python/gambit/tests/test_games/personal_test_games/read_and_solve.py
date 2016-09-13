import gambit, time, os, sys
from utils import compute_time_of

'''
Read GAME_FILE in SAVED_GAMES_DIRECTORY and create a tree from it.
'''
def create_tree(args):
    os.chdir(SAVED_GAMES_DIRECTORY)
    g = gambit.Game.read_game(GAME_FILE)
    os.chdir(PARENT_DIRECTORY)
    return g

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
    if len(sys.argv) != 2:
        print("ERROR: Please supply a filename in the {} directory".format(SAVED_GAMES_DIRECTORY))
        sys.exit(2)
    else:
    	GAME_FILE = sys.argv[1]

    # read file and create game tree
    g = compute_time_of(1, "Creating Tree", create_tree)

    # solve the game
    solutions = compute_time_of(2, "Solving Game", solve_game)

    # print the solutions to a file
    compute_time_of(3, "Printing Solutions", print_solutions)   
