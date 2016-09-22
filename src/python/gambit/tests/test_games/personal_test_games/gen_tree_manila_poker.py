# libraries that are built-in to python
import os, sys, distutils
from time import time, strftime
from distutils import util
from fractions import Fraction
from numbers import Rational
from ConfigParser import ConfigParser

# libraries from GitHub
import gambit, deuces

# custom libraries
import math_extended
from utils import compute_time_of


class Poker(gambit.Game):

    def __init__(self, 
                 MIXED_STRATEGIES,
                 ANTE, 
                 BET, 
                 RAISE,
                 LOWEST_CARD, 
                 HIGHEST_CARD, 
                 NUMBER_OF_SUITS):
        self.tree = gambit.Game.new_tree()
        self.LOWEST_CARD = LOWEST_CARD
        self.HIGHEST_CARD = HIGHEST_CARD
        self.NUMBER_OF_SUITS = NUMBER_OF_SUITS
        
        # bet and ante size
        self.ANTE  = ANTE
        self.BET   = BET
        self.RAISE = RAISE
        
        # TODO: should be moved somewhere else...
        self.MIXED_STRATEGIES = MIXED_STRATEGIES

        # need to know the size of the deck, and size of hands and board
        self.DECK_SIZE  = (HIGHEST_CARD - LOWEST_CARD + 1) * NUMBER_OF_SUITS
        self.HAND_SIZE  = 2
        self.FLOP_SIZE  = 3
        self.TURN_SIZE  = 1
        self.RIVER_SIZE = 1

        # create the outcomes
        self.NO_WINNER           = None
        self.PLAYER_1_WINS_SMALL = None
        self.PLAYER_1_WINS_BIG   = None
        self.PLAYER_2_WINS_SMALL = None
        self.PLAYER_2_WINS_BIG   = None

        # this will hold the cards that are currently being considered in the game
        self.cards_in_play = [None, None, None, None, None, None, None]


def create_game(args):

    # try to get user input
    MINIMUM_DECK_SIZE = 7
    USAGE_OUTPUT = """
    Usage: python gen_tree_simple [PLAYER_1 (str)
                                   PLAYER_2 (str)
                                   MIXED_STRATEGIES (bool)
                                   ANTE (int > 0)
                                   BET (int > 0)
                                   RAISE (int > 0)
                                   LOWEST_CARD (int: 2->13)
                                   HIGHEST_CARD (int: LOWEST_CARD->14)
                                   NUMBER_OF_SUITS (int: 1->4)]
    Deck must contain at least {} cards.""".format(MINIMUM_DECK_SIZE)

    try:
        
        if len(sys.argv)    == 1:

            # create the configuration parser
            CONFIGURATION_FILE = "config.ini"
            cfg = ConfigParser()
            cfg.read(CONFIGURATION_FILE)

            GAME_SECTION     = "game"
            POKER_SECTION    = "poker"
            MANILA_SECTION   = "manila"
            PERSONAL_SECTION = "personal"
            PLAYER_1         = cfg.get(GAME_SECTION,"PLAYER_1")
            PLAYER_2         = cfg.get(GAME_SECTION,"PLAYER_2")
            MIXED_STRATEGIES = distutils.util.strtobool(cfg.get(GAME_SECTION,"MIXED_STRATEGIES"))
            ANTE             = int(cfg.get(POKER_SECTION,"ANTE"))
            BET              = int(cfg.get(POKER_SECTION,"BET"))
            RAISE            = int(cfg.get(POKER_SECTION,"RAISE"))
            LOWEST_CARD      = int(cfg.get(MANILA_SECTION,"LOWEST_CARD"))
            HIGHEST_CARD     = int(cfg.get(PERSONAL_SECTION,"HIGHEST_CARD"))
            NUMBER_OF_SUITS  = int(cfg.get(PERSONAL_SECTION,"NUMBER_OF_SUITS"))
        
        # values added as arguments
        elif len(sys.argv)  == 10:
            PLAYER_1         = sys.argv[1]
            PLAYER_2         = sys.argv[2]
            MIXED_STRATEGIES = distutils.util.strtobool(sys.argv[3])
            ANTE             = int(sys.argv[4])
            BET              = int(sys.argv[5])
            RAISE            = int(sys.argv[6])
            LOWEST_CARD      = int(sys.argv[7])
            HIGHEST_CARD     = int(sys.argv[8])
            NUMBER_OF_SUITS  = int(sys.argv[9])
        
        # improper amount of values added
        else:    
            raise ValueError
        
        # extra checks
        if (ANTE < 0 or 
            BET < 0 or 
            RAISE < 0 or 
            LOWEST_CARD < 2 or 
            LOWEST_CARD > 13 or 
            HIGHEST_CARD <= LOWEST_CARD or 
            HIGHEST_CARD > 14 or 
            NUMBER_OF_SUITS < 1 or 
            NUMBER_OF_SUITS > 4 or
            (HIGHEST_CARD-LOWEST_CARD+1)*NUMBER_OF_SUITS < MINIMUM_DECK_SIZE):
           raise ValueError
    
    except ValueError:
        print(USAGE_OUTPUT)
        sys.exit(2)

    # create the poker game
    g = Poker(MIXED_STRATEGIES=MIXED_STRATEGIES,
              ANTE=ANTE, 
              BET=BET, 
              RAISE=RAISE,
              LOWEST_CARD=LOWEST_CARD, 
              HIGHEST_CARD=HIGHEST_CARD, 
              NUMBER_OF_SUITS=NUMBER_OF_SUITS)

    # create the title and players
    g.tree.players.add(PLAYER_1)
    g.tree.players.add(PLAYER_2)
    TITLE_FORMAT = "PSP Game with {} players and cards from range {} to {} (via tree-method)"
    g.tree.title = TITLE_FORMAT.format(len(g.tree.players), LOWEST_CARD, HIGHEST_CARD)

    # create the outcomes
    g.NO_WINNER           = multiply_outcome(g, "No Winner",  0)
    g.PLAYER_1_WINS_SMALL = multiply_outcome(g, "Player 1 Wins Small",  1)
    g.PLAYER_1_WINS_BIG   = multiply_outcome(g, "Player 1 Wins Big",    3)
    g.PLAYER_2_WINS_SMALL = multiply_outcome(g, "Player 2 Wins Small", -1)
    g.PLAYER_2_WINS_BIG   = multiply_outcome(g, "Player 2 Wins Big",   -3)

    # we're done setting up the game
    return g


def create_tree(args):

    print("Beginning to compute payoff tree".format(g.tree.title))

    # Chance node set probability of each chance action
    NUMBER_OF_PLAYERS       = len(g.tree.players)
    HOLE_CARDS              = g.HAND_SIZE * NUMBER_OF_PLAYERS
    HOLE_CARDS_COMBINATIONS = math_extended.combinations(g.DECK_SIZE, g.HAND_SIZE) * \
                              math_extended.combinations(g.DECK_SIZE - g.HAND_SIZE, g.HAND_SIZE)

    # create the cards
    CARD_LABELS = create_card_labels(g)
    
    # create the chance node and set the number of nodes
    total_start_time = time()
    start_time = time()
    print "Number of combinations: {}".format(HOLE_CARDS_COMBINATIONS)
    iset_r1 = g.tree.root.append_move(g.tree.players.chance, HOLE_CARDS_COMBINATIONS)
    
    # for each possible hand for player 1...
    hole_cards_deal_branch_counter = -1
    infoset_counter = -1
    for index_card1 in range(len(CARD_LABELS)-1):
        print("Number of branches completed: {}".format(hole_cards_deal_branch_counter))
        print("Time taken to create these branches: {} seconds".format(time() - start_time))
        start_time = time()
        for index_card2 in range(index_card1+1, len(CARD_LABELS)):
            g.cards_in_play[0] = CARD_LABELS[index_card1]
            g.cards_in_play[1] = CARD_LABELS[index_card2]
            CARD_LABELS_MINUS_PLAYER_1_CARDS = CARD_LABELS[:index_card1] +              \
                                               CARD_LABELS[index_card1+1:index_card2] + \
                                               CARD_LABELS[index_card2+1:]
            
            # ... and for each possible hand for player 2...
            for index_card3 in range(len(CARD_LABELS_MINUS_PLAYER_1_CARDS)-1):
                for index_card4 in range(index_card3+1, len(CARD_LABELS_MINUS_PLAYER_1_CARDS)):
                    g.cards_in_play[2] = CARD_LABELS_MINUS_PLAYER_1_CARDS[index_card3]
                    g.cards_in_play[3] = CARD_LABELS_MINUS_PLAYER_1_CARDS[index_card4]
                    CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS = CARD_LABELS_MINUS_PLAYER_1_CARDS[:index_card3] +              \
                                                             CARD_LABELS_MINUS_PLAYER_1_CARDS[index_card3+1:index_card4] + \
                                                             CARD_LABELS_MINUS_PLAYER_1_CARDS[index_card4+1:]

                    # ... we need to create a branch for that chance action. 
                    hole_cards_deal_branch_counter += 1
                    iset_round1_label = "{} - {},{}; {} - {},{}".format(g.tree.players[0].label, 
                                                                        g.cards_in_play[0], 
                                                                        g.cards_in_play[1], 
                                                                        g.tree.players[1].label, 
                                                                        g.cards_in_play[2], 
                                                                        g.cards_in_play[3])
                    iset_r1.actions[hole_cards_deal_branch_counter].label = iset_round1_label
                    
                    # for each chance action, we need to create player 1's betting and checking branches
                    iset = g.tree.root.children[hole_cards_deal_branch_counter].append_move(g.tree.players[0], 2)
                    iset.label = "{}'s' Decision Node".format(g.tree.players[0].label)
                    iset.actions[0].label = "{} bets".format(g.tree.players[0].label)
                    iset.actions[1].label = "{} checks".format(g.tree.players[0].label)

                    # at the end of player 1's betting branch, 
                    # we need to create a player 2's choice node that has calling and a folding branches
                    iset = g.tree.root.children[hole_cards_deal_branch_counter].children[0].append_move(g.tree.players[1], 2)
                    iset.label = "{}'s' Response Node".format(g.tree.players[1].label)
                    iset.actions[0].label = "{} calls".format(g.tree.players[1].label)
                    iset.actions[1].label = "{} folds".format(g.tree.players[1].label)

                    # at the end of player 1's betting branch, 
                    # we need to create a player 2's choice node that has calling and a folding branches
                    iset = g.tree.root.children[hole_cards_deal_branch_counter].children[1].append_move(g.tree.players[1], 2)
                    iset.label = "{}'s' Response Node".format(g.tree.players[1].label)
                    iset.actions[0].label = "{} checks".format(g.tree.players[1].label)

                    # handle the flop when player 1 checks
                    handle_flop(g, CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS, hole_cards_deal_branch_counter, False)

                    # handle the flop when player 1 bets and player 2 calls
                    handle_flop(g, CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS, hole_cards_deal_branch_counter, True)

    print ("Completed making the tree in {} seconds.".format(time() - start_time))
    return g


def handle_flop(g, CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS, i, p1_bet):
    
    # we need the number of possible flop combinations
    NUMBER_OF_PLAYERS       = len(g.tree.players)
    HOLE_CARDS              = g.HAND_SIZE * NUMBER_OF_PLAYERS
    FLOP_COMBINATIONS       = math_extended.combinations(g.DECK_SIZE - HOLE_CARDS, g.FLOP_SIZE)

    # create the chance node and set the number of nodes
    if p1_bet:
        iset = g.tree.root.children[i].children[0].children[0].append_move(g.tree.players.chance, FLOP_COMBINATIONS)
    else:
        iset = g.tree.root.children[i].children[1].children[0].append_move(g.tree.players.chance, FLOP_COMBINATIONS)

    # iset = p2_node.append_move(g.tree.players.chance, FLOP_COMBINATIONS)

    # for each possible flop...
    j = -1
    for index_card5 in range(len(CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS)-2):
        for index_card6 in range(index_card5+1, len(CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS)-1):
            for index_card7 in range(index_card6+1, len(CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS)):
                g.cards_in_play[4] = CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[index_card5]
                g.cards_in_play[5] = CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[index_card6]
                g.cards_in_play[6] = CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[index_card7]
                CARD_LABELS_MINUS_PLAYER_1_AND_2_AND_FLOP_CARDS = CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[:index_card5] +              \
                                                                  CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[index_card5+1:index_card6] + \
                                                                  CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[index_card6+1:index_card7] + \
                                                                  CARD_LABELS_MINUS_PLAYER_1_AND_2_CARDS[index_card7+1:]

                # ... we need to create a branch for that chance action. 
                j += 1
                iset_round2_label = "{}, {}, {}".format(g.cards_in_play[4], g.cards_in_play[5], g.cards_in_play[6])
                iset.actions[j].label = iset_round2_label

                # calculate payoffs
                if p1_bet:
                    child = g.tree.root.children[i].children[0].children[0].children[j]
                else:
                    child = g.tree.root.children[i].children[1].children[0].children[j]
                winner = calculate_winner(g)
                if winner == g.tree.players[0]:
                    if p1_bet:
                        child.outcome = g.PLAYER_1_WINS_SMALL
                    else:
                        child.outcome = g.PLAYER_1_WINS_BIG
                elif winner == g.tree.players[1]:
                    if p1_bet:
                        child.outcome = g.PLAYER_2_WINS_SMALL
                    else:
                        child.outcome = g.PLAYER_2_WINS_BIG
                else:
                    child.outcome = g.NO_WINNER


def create_card_labels(g):
    '''
    Takes the cards ranks and suits we're interested in and creates card labels from them.
    Example: 
    CARD_RANKS  = ['Q', 'K', 'A']
    CARD_SUITS  = ['s','c','d','h']
    CARD_LABELS = ['Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']
    '''

    from itertools import product
    CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    CARD_RANKS_IN_THIS_GAME = CARD_RANKS[g.LOWEST_CARD-2 : g.HIGHEST_CARD-1]
    CARD_SUITS = ['s','c','d','h']
    CARD_SUITS_IN_THIS_GAME = CARD_SUITS[ -g.NUMBER_OF_SUITS + 4:]
    SEPARATOR = ""
    CARD_LABELS = [SEPARATOR.join(map(str,card_rank_suit_tuple)) for card_rank_suit_tuple in product(CARD_RANKS_IN_THIS_GAME, CARD_SUITS_IN_THIS_GAME)]
    return CARD_LABELS


def multiply_outcome(g, description, multiple):
    '''
    Takes the default outcome and multiplies it based on the bet value.
    '''

    new_outcome = g.tree.outcomes.add("Default outcome multiplied by {}".format(multiple))
    new_outcome[0] =  multiple
    new_outcome[1] = -multiple
    return new_outcome


def calculate_winner(g):
    '''
    Given 5 cards, calculates who has the stronger hand.
    '''
    player_1_hand = [
        deuces.Card.new(g.cards_in_play[0]),
        deuces.Card.new(g.cards_in_play[1])
    ]
    player_2_hand = [
        deuces.Card.new(g.cards_in_play[2]),
        deuces.Card.new(g.cards_in_play[3])
    ]
    board = [
        deuces.Card.new(g.cards_in_play[4]),
        deuces.Card.new(g.cards_in_play[5]),
        deuces.Card.new(g.cards_in_play[6])
    ]

    evaluator = deuces.Evaluator()
    player_1_hand_value = evaluator.evaluate(board, player_1_hand)
    player_2_hand_value = evaluator.evaluate(board, player_2_hand)
    if player_1_hand_value < player_2_hand_value:
        return g.tree.players[0]
    elif player_1_hand_value > player_2_hand_value:
        return g.tree.players[1]
    else:
        return None


def solve_game(args):
    '''
    Solve the game.
    '''

    # choose the solver needed for this game
    if MIXED_STRATEGIES == True:
        solver = gambit.nash.ExternalEnumMixedSolver()
    else:
        solver = gambit.nash.ExternalEnumPureSolver()
    
    # solve game
    solutions = solver.solve(g.tree)
    return solutions


def print_solutions(args):
    '''
    Create a solutions directory, if necessary, and save the solutions there.
    '''
    
    # create directory and cd in
    if not os.path.exists(SOLUTIONS_DIRECTORY):
        os.mkdir(SOLUTIONS_DIRECTORY)
    os.chdir(SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP-Solutions.nfg".format(strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    for solution in solutions:
        target_file.write("{}\n".format(str(solution)))
    
    # go back out
    os.chdir(PARENT_DIRECTORY)


def print_game(args):
    '''
    Create a solutions directory, if necessary, and save the solutions there.
    '''

    # create directory and cd in
    if not os.path.exists(SOLUTIONS_DIRECTORY):
        os.mkdir(SOLUTIONS_DIRECTORY)
    os.chdir(SOLUTIONS_DIRECTORY)

    # create file
    file_name = "{}-PSP-Game.nfg".format(strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    
    # print solutions
    target_file.write("{}".format(g.tree.write()))
    
    # go back out
    os.chdir(PARENT_DIRECTORY)

if __name__ == '__main__':

    # directory names
    PARENT_DIRECTORY = ".."
    SAVED_GAMES_DIRECTORY = "saved"
    SOLUTIONS_DIRECTORY = "Solutions-for-PSP-Games-{}".format(strftime("%Y-%m-%d %H:%M:%S"))

    # create the game tree, solve the game, print the solutions to a file, print the game
    g = compute_time_of(1, "Initializing Game", create_game, sys.argv)
    g = compute_time_of(2, "Creating Tree", create_tree, g)
    # solutions = compute_time_of(3, "Solving Game", solve_game, g)
    # compute_time_of(4, "Printing Solutions", print_solutions, solutions) 
    compute_time_of(5, "Printing Game", print_game, g)