import os
from gambit import nash
from utils import compute_time_of
from time import time, strftime
from ConfigParser import ConfigParser


class Saver(object):

    def __init__(self,
                 PARENT_DIRECTORY, 
                 SAVED_GAMES_DIRECTORY, 
                 SOLUTIONS_DIRECTORY):

        # paths
        self.PARENT_DIRECTORY      = PARENT_DIRECTORY
        self.SAVED_GAMES_DIRECTORY = SAVED_GAMES_DIRECTORY
        self.SOLUTIONS_DIRECTORY   = SOLUTIONS_DIRECTORY


def create_saver():

    # read the configuration file
    CONFIGURATION_FILE = "config.ini"
    cfg = ConfigParser()
    cfg.read(CONFIGURATION_FILE)

    # directory names
    FILES_SECTION         = "files-paths"
    PARENT_DIRECTORY      = cfg.get(FILES_SECTION,"PARENT_DIRECTORY")
    SAVED_GAMES_DIRECTORY = cfg.get(FILES_SECTION,"SAVED_GAMES_DIRECTORY")
    SOLUTIONS_DIRECTORY   = cfg.get(FILES_SECTION,"SOLUTIONS_DIRECTORY").format(strftime("%Y-%m-%d %H:%M:%S"))

    s = Saver(PARENT_DIRECTORY=PARENT_DIRECTORY, 
              SAVED_GAMES_DIRECTORY=SAVED_GAMES_DIRECTORY, 
              SOLUTIONS_DIRECTORY=SOLUTIONS_DIRECTORY)

    return s


def solve_game(g):
    '''
    Solve the game.
    '''

    # choose the solver needed for this game
    if g.MIXED_STRATEGIES == True:
        solver = nash.ExternalEnumMixedSolver()
    else:
        solver = nash.ExternalEnumPureSolver()
    
    # solve game
    solutions = solver.solve(g.tree)
    return solutions


def print_solutions(solutions, s):
    '''
    Create a solutions directory, if necessary, and save the solutions there.
    '''
    
    # create directory and cd in
    if not os.path.exists(s.SOLUTIONS_DIRECTORY):
        os.mkdir(s.SOLUTIONS_DIRECTORY)
    os.chdir(s.SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP-Solutions.nfg".format(strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    for solution in solutions:
        target_file.write("{}\n".format(str(solution)))
    
    # go back out
    os.chdir(s.PARENT_DIRECTORY)


def print_game(g, s):
    '''
    Create a solutions directory, if necessary, and save the solutions there.
    '''

    # create directory and cd in
    if not os.path.exists(s.SOLUTIONS_DIRECTORY):
        os.mkdir(s.SOLUTIONS_DIRECTORY)
    os.chdir(s.SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP-Game.nfg".format(strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    target_file.write("{}".format(g.tree.write()))
    
    # go back out
    os.chdir(s.PARENT_DIRECTORY)
