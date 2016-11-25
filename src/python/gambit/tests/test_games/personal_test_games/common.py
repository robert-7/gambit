import os
from gambit import nash
from utils import compute_time_of
from time import time, strftime
from ConfigParser import ConfigParser
from distutils    import util

class Saver(object):

    def __init__(self):

        # read the configuration file
        CONFIGURATION_FILE = "config.ini"
        cfg = ConfigParser()
        cfg.read(CONFIGURATION_FILE)

        # directory names
        FILES_SECTION                      = "files-paths"
        self.PARENT_DIRECTORY              = cfg.get(FILES_SECTION, "PARENT_DIRECTORY")
        self.SAVED_GAMES_DIRECTORY         = cfg.get(FILES_SECTION, "SAVED_GAMES_DIRECTORY")
        self.OUTPUTS_DIRECTORY             = cfg.get(FILES_SECTION, "OUTPUTS_DIRECTORY")
        OUTPUT_DIRECTORY                   = cfg.get(FILES_SECTION, "OUTPUT_DIRECTORY")
        self.OUTPUT_DIRECTORY              = OUTPUT_DIRECTORY.format(strftime("%Y-%m-%d %H:%M:%S"))
        self.EXPECTED_VALUES_FILE          = cfg.get(FILES_SECTION, "EXPECTED_VALUES_FILE")
        PRINT_ORIGINAL_GAME_TREE           = cfg.get(FILES_SECTION, "PRINT_ORIGINAL_GAME_TREE")
        self.PRINT_ORIGINAL_GAME_TREE      = util.strtobool(PRINT_ORIGINAL_GAME_TREE)
        self.ORIGINAL_GAME_TREE_FILE       = cfg.get(FILES_SECTION, "ORIGINAL_GAME_TREE_FILE")
        PRINT_PRUNED_GAME_TREE             = cfg.get(FILES_SECTION, "PRINT_PRUNED_GAME_TREE")
        self.PRINT_PRUNED_GAME_TREE        = util.strtobool(PRINT_PRUNED_GAME_TREE)
        self.PRUNED_GAME_TREE_FILE         = cfg.get(FILES_SECTION, "PRUNED_GAME_TREE_FILE")
        PRINT_UNDOMINATED_GAME_MATRIX      = cfg.get(FILES_SECTION, "PRINT_UNDOMINATED_GAME_MATRIX")
        self.PRINT_UNDOMINATED_GAME_MATRIX = util.strtobool(PRINT_UNDOMINATED_GAME_MATRIX)
        self.UNDOMINATED_GAME_MATRIX_FILE  = cfg.get(FILES_SECTION, "PRUNED_GAME_TREE_FILE")
        PRINT_NFG_FORMAT                   = cfg.get(FILES_SECTION, "PRINT_NFG_FORMAT")
        self.PRINT_NFG_FORMAT              = util.strtobool(PRINT_NFG_FORMAT)
        PRINT_GTE_FORMAT                   = cfg.get(FILES_SECTION, "PRINT_GTE_FORMAT")
        self.PRINT_GTE_FORMAT              = util.strtobool(PRINT_GTE_FORMAT)
        SOLVE_GAME                         = cfg.get(FILES_SECTION, "SOLVE_GAME")
        self.SOLVE_GAME                    = util.strtobool(SOLVE_GAME)
        self.SOLUTIONS_FILE                = cfg.get(FILES_SECTION, "SOLUTIONS_FILE")


def create_saver():

    # create the saver object
    s = Saver()

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


def print_expected_values(g, s, iset):

    # create outputs directory, if necessary, and cd in
    safe_cd(s.OUTPUTS_DIRECTORY)

    # create output directory, if necessary, and cd in
    safe_cd(s.OUTPUT_DIRECTORY)

    # we need a "mixed behavior profile" which helps us assign probability
    # distributions over the actions at each information set:
    # http://gambit.sourceforge.net/gambit15/pyapi.html
    #                               #mixed-strategy-and-behavior-profiles
    # This differs from a "mixed strategy profile" in that the former
    # applies to actions whereas the lineatter applies to strategies.
    p = g.tree.mixed_behavior_profile(rational=True)

    # we want to write this to a file
    file_name = s.EXPECTED_VALUES_FILE
    target_file = open(file_name, 'w')

    # for each action in which we're interested...
    for action in iset.actions:
    
        # use the profile on an information set to get the payoff
        line_template = "Action ({}) - Payoff ({})\n"
        line = line_template.format(action.label, p.payoff(action))

        # print to a file
        target_file.write(line)

    # close the target file
    target_file.close()

    # go back out
    os.chdir(s.PARENT_DIRECTORY)
    os.chdir(s.PARENT_DIRECTORY)


def print_solutions(solutions, s):
    '''
    Create a solutions directory, if necessary, and save the solutions there.
    '''
    
    # create outputs directory, if necessary, and cd in
    safe_cd(s.OUTPUTS_DIRECTORY)

    # create output directory, if necessary, and cd in
    safe_cd(s.OUTPUT_DIRECTORY)

    # create file
    file_name = s.SOLUTIONS_FILE
    target_file = open(file_name, 'w')
    
    # print solutions
    for solution in solutions:
        target_file.write("{}\n".format(str(solution)))
    
    # close the target file
    target_file.close()

    # go back out
    os.chdir(s.PARENT_DIRECTORY)
    os.chdir(s.PARENT_DIRECTORY)


def print_game(g, s, base_name):
    '''
    Create a solutions directory, if necessary, and save the solutions there.
    '''

    def _print_game(path_template, extension, output_format):
        '''
        Print the game.
        '''

        # base name with extension
        path = path_template.format(extension)

        # create file
        target_file = open(path, 'w')
        
        # print solutions
        target_file.write("{}".format(g.tree.write(output_format)))
        
        # close the target file
        target_file.close()


    # create outputs directory, if necessary, and cd in
    safe_cd(s.OUTPUTS_DIRECTORY)

    # create output directory, if necessary, and cd in
    safe_cd(s.OUTPUT_DIRECTORY)

    path_template = base_name + ".{}"

    # print game in .nfg format
    if s.PRINT_NFG_FORMAT:
        _print_game(path_template=path_template, extension="nfg", output_format="native")
    
    # print game in .gte format
    if s.PRINT_GTE_FORMAT:
        _print_game(path_template=path_template, extension="gte", output_format="gte")

    # go back out
    os.chdir(s.PARENT_DIRECTORY)
    os.chdir(s.PARENT_DIRECTORY)


def safe_cd(d):

    # create outputs directory and cd in
    if not os.path.exists(d):
        os.mkdir(d)
    os.chdir(d)