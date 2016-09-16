import gambit, math, time, os, sys
import math_extended
from utils import compute_time_of
from fractions import Fraction
from numbers import Rational
import itertools

def create_tree(args):
    '''
    Usage: 
    gen.psp(num_cards=7, title="PSP Game with 2 Players and 7 Cards", player_names=["Rose","Colin"], ante=1, bet=2)
    '''

    # player 1 can bet or check, while player 2 can either call or fold
    NUM_CHOICES_PER_CARD = 2

    # need to know how many cards we have
    DECK_SIZE  = (HIGHEST_CARD - LOWEST_CARD + 1) * NUMBER_OF_SUITS
    HAND_SIZE  = 2
    FLOP_SIZE  = 3
    TURN_SIZE  = 1
    RIVER_SIZE = 1
    
    # create the game, and add the title and players
    g = gambit.Game.new_tree()
    g.title = TITLE
    g.players.add(PLAYER_1)
    g.players.add(PLAYER_2)
    print("Beginning to compute payoff tree".format(g.title))

    # Chance node set probability of each chance action
    HOLE_CARDS_COMBINATIONS = math_extended.combinations(DECK_SIZE, HAND_SIZE * NUMBER_OF_PLAYERS)

    # create the cards
    CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    CARD_RANKS_IN_THIS_GAME = CARD_RANKS[LOWEST_CARD - 2, HIGHEST_CARD - 1]
    CARD_SUITS = ['s','c','d','h']
    CARD_SUITS_IN_THIS_GAME = CARD_SUITS[ -NUMBER_OF_SUITS + 4:]
    CARD_LABELS = itertools.product(CARD_RANKS_IN_THIS_GAME, CARD_SUITS_IN_THIS_GAME)

    # create the chance node and set the number of nodes
    iset = g.root.append_move(g.players.chance, HOLE_CARDS_COMBINATIONS)
    
    # for each possible hand for player 1...
    chance_branch_counter = -1
    for index_card1 in range(len(CARD_LABELS)-1):
        for index_card2 in range(index_card1+1, len(CARD_LABELS)):
            card1 = CARD_LABELS[index_card1]
            card2 = CARD_LABELS[index_card2]
            CARD_LABELS_MINUS_PLAYER_1_CARDS = CARD_LABELS[:index_card1] + 
                                               CARD_LABELS[index_card1+1:index_card2] +
                                               CARD_LABELS[index_card2+1:]
            
            # ... and for each possible hand for player 2...
            for index_card3 in range(len(CARD_LABELS_MINUS_PLAYER_1_CARDS)-1):
                for index_card4 in range(index_card3+1, len(CARD_LABELS)):
                    card3 = CARD_LABELS[index_card3]
                    card4 = CARD_LABELS[index_card4]
                    CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS = CARD_LABELS[:index_card3] + 
                                                             CARD_LABELS[index_card3+1:index_card4] +
                                                             CARD_LABELS[index_card4+1:]
                    
                    # ... we need to create a branch for that chance action. 
                    chance_branch_counter++
                    iset.actions[chance_branch_counter].label = "{} - {},{}; {} - {},{}"
                                                         .format(g.players[0].label, 
                                                                 card1, card2, 
                                                                 g.players[1].label, 
                                                                 card3, card4)
                    
                    # for each chance action, we need to create player 1's betting and checking branches
                    iset = g.root.children[0].append_move(g.players[PLAYER_1], 2)
                    iset.actions[0].label = iset.actions[chance_branch_counter].label + "; {} bets".format(g.players[0])
                    iset.actions[1].label = iset.actions[chance_branch_counter].label + "; {} checks".format(g.players[0])

                    # at the end of player 1's betting branch, we need to create a player 2's choice node that has a calling and a folding branches
                    iset = g.root.children[0].children[0].append_move(g.players[PLAYER_2], 2)
                    iset.label = "{} has A and {}".format(PLAYER_1, "Bet 1")
                    iset.actions[0].label = "Yes"
                    iset.actions[1].label = "No"


    # games are created by a list, here called num_strats_per_player
    # the length of num_strats_per_player determines the number of players
    # while ints of num_strats_per_player determines the number of strategies each player will have
    num_strats_per_player=[]
    for i in range(num_players):
        num_strats = math.pow(NUM_CHOICES_PER_CARD, num_cards)
        num_strats_per_player.append(num_strats)

'''
Solve the game.
'''
def solve_game(args):

    # choose the solver needed for this game
    if MIXED_STRATEGIES == True:
        solver = gambit.nash.ExternalEnumMixedSolver()
    else:
        solver = gambit.nash.ExternalEnumPureSolver()
    
    # solve game
    solutions = solver.solve(g)
    return solutions

'''
Create a solutions directory, if necessary, and save the solutions there.
'''
def print_solutions(args):
    
    # create directory and cd in
    if not os.path.exists(SOLUTIONS_DIRECTORY):
        os.mkdir(SOLUTIONS_DIRECTORY)
    os.chdir(SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP-Solutions.nfg".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    for solution in solutions:
        target_file.write("{}\n".format(str(solution)))
    
    # go back out
    os.chdir(PARENT_DIRECTORY)

'''
Create a solutions directory, if necessary, and save the solutions there.
'''
def print_game(args):
    
    # create directory and cd in
    if not os.path.exists(SOLUTIONS_DIRECTORY):
        os.mkdir(SOLUTIONS_DIRECTORY)
    os.chdir(SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP-Game.nfg".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    target_file.write("{}".format(g.write()))
    
    # go back out
    os.chdir(PARENT_DIRECTORY)

if __name__ == '__main__':

    # directory names
    PARENT_DIRECTORY = ".."
    SAVED_GAMES_DIRECTORY = "saved"
    SOLUTIONS_DIRECTORY = "Solutions-for-PSP-Games-{}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    NUMBER_OF_PLAYERS = 2

    # get user info
    if len(sys.argv)    == 1:
        PLAYER_1_NAME    = "Rose"
        PLAYER_2_NAME    = "Colin"
        LOWEST_CARD      = 12
        HIGHEST_CARD     = 14
        NUMBER_OF_SUITS  = 4
        ANTE             = 1
        BET              = 2
        MIXED_STRATEGIES = True
    elif len(sys.argv)  == 9:
        PLAYER_1         = sys.argv[1]
        PLAYER_2         = sys.argv[2]
        LOWEST_CARD      = sys.argv[3]
        HIGHEST_CARD     = sys.argv[4]
        NUMBER_OF_SUITS  = sys.argv[5]
        ANTE             = sys.argv[6]
        BET              = sys.argv[7]
        MIXED_STRATEGIES = sys.argv[8]
    else:    
        print("Usage: python gen_tree_simple [PLAYER_1_NAME\n"+
              "                               PLAYER_2_NAME\n"+
              "                               LOWEST_CARD\n"+
              "                               HIGHEST_CARD\n"+
              "                               NUMBER_OF_SUITS\n"+
              "                               ANTE\n"+
              "                               BET\n"+
              "                               MIXED_STRATEGIES]")
        sys.exit(2)

    TITLE = "PSP Game with {} players and cards from range {} to {} (via tree-method)".format(NUMBER_OF_PLAYERS, LOWEST_CARD, HIGHEST_CARD)

    # generate the strategies
    for n in range(2, 5):
    
        # create the tree, solve the game, print the solutions to a file, print the game
        g = compute_time_of(1, "Creating Tree", create_tree)
        solutions = compute_time_of(2, "Solving Game", solve_game)
        compute_time_of(3, "Printing Solutions", print_solutions) 
        compute_time_of(4, "Printing Game", print_game)
