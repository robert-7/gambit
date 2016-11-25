# libraries that are built-in to python
import sys, distutils
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
import common


class Poker(gambit.Game):

    def __init__(self, 
                 MIXED_STRATEGIES,
                 ANTE, 
                 BET, 
                 RAISE,
                 LOWEST_CARD, 
                 HIGHEST_CARD, 
                 NUMBER_OF_SUITS):

        # card values
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

        self.tree      = None
        self.bst_hole  = None
        self.bst_flop  = None
        self.bst_turn  = None
        self.bst_river = None
        self.cst_hole  = None
        self.cst_flop  = None
        self.cst_turn  = None
        self.cst_river = None


def create_game(cfg):

    # we need to stop the script if they never specified enough cards
    # MINIMUM_DECK_SIZE = (g.HAND_SIZE * len(g.tree.players)) + g.FLOP_SIZE + g.TURN_SIZE + g.RIVER_SIZE
    # MINIMUM_DECK_SIZE = ( 2 * 2 ) + 3 + 1 + 1
    MINIMUM_DECK_SIZE = ( 2 * 2 ) + 3 + 1

    # try to get user input
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
    
    # stop the script if anything went wrong
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
    
    # create the tree, title, and players
    g.tree = gambit.Game.new_tree()
    g.tree.players.add(PLAYER_1)
    g.tree.players.add(PLAYER_2)
    TITLE_FORMAT = "PSP Game with {} players and cards from range {} to {} (via tree-method)"
    g.tree.title = TITLE_FORMAT.format(len(g.tree.players), LOWEST_CARD, HIGHEST_CARD)

    # create the branches for the templates
    # g.tree.root.children[0] = bst_river
    # g.tree.root.children[1] = cst_river
    # g.tree.root.children[2] = bst_turn
    # g.tree.root.children[3] = cst_turn
    # g.tree.root.children[4] = bst_flop
    # g.tree.root.children[5] = cst_flop
    # g.tree.root.children[6] = bst_hole
    # g.tree.root.children[7] = cst_hole
    g.tree.root.append_move(g.tree.players.chance, 8)

    # create the outcomes
    # g.NO_WINNER           = multiply_outcome(g, "No Winner",  0)
    # g.PLAYER_1_WINS_SMALL = multiply_outcome(g, "Player 1 Wins Small",  1)
    # g.PLAYER_1_WINS_BIG   = multiply_outcome(g, "Player 1 Wins Big",    3)
    # g.PLAYER_2_WINS_SMALL = multiply_outcome(g, "Player 2 Wins Small", -1)
    # g.PLAYER_2_WINS_BIG   = multiply_outcome(g, "Player 2 Wins Big",   -3)

    # create the bst tree templates
    create_bst(g, PLAYER_1, PLAYER_2)
    g.tree.root.children[2].copy_tree(g.tree.root.children[0])
    g.tree.root.children[4].copy_tree(g.tree.root.children[0])
    g.tree.root.children[6].copy_tree(g.tree.root.children[0])

    # create the cst's for the hole, flop, turn, and river rounds
    number_of_cards_remaining = create_cst(g, g.tree.root.children[7], PLAYER_1, PLAYER_2, g.HAND_SIZE, g.DECK_SIZE, len(g.tree.players))
    number_of_cards_remaining = create_cst(g, g.tree.root.children[5], PLAYER_1, PLAYER_2, g.FLOP_SIZE, number_of_cards_remaining)
    number_of_cards_remaining = create_cst(g, g.tree.root.children[3], PLAYER_1, PLAYER_2, g.TURN_SIZE, number_of_cards_remaining)
    number_of_cards_remaining = create_cst(g, g.tree.root.children[1], PLAYER_1, PLAYER_2, g.RIVER_SIZE, number_of_cards_remaining)

    # we're done setting up the game
    return g


def create_cst(g, cst_tree, PLAYER_1, PLAYER_2, number_of_cards_to_choose, number_of_cards_remaining, number_of_dealings=1):
    
    # we need to keep track of the number of branches we'll need
    CARDS_COMBINATIONS = 1

    for number in range(number_of_dealings):
        
        # Calculate the number of card combinations for this round of cards getting flipped
        CARDS_COMBINATIONS *= math_extended.combinations(number_of_cards_remaining, number_of_cards_to_choose)

        # update number_of_cards_remaining 
        number_of_cards_remaining -= number_of_cards_to_choose

    # create the branches
    cst_tree.append_move(g.tree.players.chance, CARDS_COMBINATIONS)

    print "Created cst with this number of combinations: {}".format(CARDS_COMBINATIONS)

    return number_of_cards_remaining


def create_bst(g, PLAYER_1, PLAYER_2):
    
    # create the bst tree template
    bst_river_branch = g.tree.root.children[0]
    bst_river_branch.label = "{}'s' Decision Node".format(g.tree.players[0].label)

    # we need to create player 1's betting and checking branches
    p1_iset = bst_river_branch.append_move(g.tree.players[0], 2)
    p1_iset.actions[0].label = "{} bets".format(g.tree.players[0].label)
    p1_iset.actions[1].label = "{} checks".format(g.tree.players[0].label)

    # at the end of player 1's betting branch, 
    # we need to create a player 2's choice node that has calling and a folding branches
    bst_river_branch.children[0].label = "{}'s Response Node given {} Bet".format(g.tree.players[1].label, g.tree.players[0].label)
    p1_bet_p2_iset = bst_river_branch.children[0].append_move(g.tree.players[1], 2)
    p1_bet_p2_iset.actions[0].label = "{} calls".format(g.tree.players[1].label)
    p1_bet_p2_iset.actions[1].label = "{} folds".format(g.tree.players[1].label)

    # at the end of player 1's calling branch, 
    # we want to label the node -- but we want add any branches yet TODO: Add Betting/Checking Branches
    p1_check_p2_iset = bst_river_branch.children[1].label = "{}'s Response Node given {} Checked".format(g.tree.players[1].label, g.tree.players[0].label)


def create_tree(args):
    
    # 1) copy bst_river subtree to all children of cst_river
    compute_time_of("a", "Copying {} to {}".format(0, 1), copy_bst_to_cst, (g, 0))

    # 2) copy cst_river subtree to children[0].children[0] and children[1] of bst_turn
    compute_time_of("b", "Copying {} to {}".format(1, 2), copy_cst_to_bst, (g, 1))

    # 3) copy bst_turn subtree to all children of cst_turn
    compute_time_of("c", "Copying {} to {}".format(2, 3), copy_bst_to_cst, (g, 2))

    # 4) copy cst_turn subtree to children[0].children[0] and children[1] of bst_flop
    compute_time_of("d", "Copying {} to {}".format(3, 4), copy_cst_to_bst, (g, 3))

    # 5) copy bst_flop subtree to all children of cst_flop
    compute_time_of("e", "Copying {} to {}".format(4, 5), copy_bst_to_cst, (g, 4))

    # 6) copy cst_flop subtree to children[0].children[0] and children[1] of bst_hole
    compute_time_of("f", "Copying {} to {}".format(5, 6), copy_cst_to_bst, (g, 5))

    # 7) copy bst_hole subtree to all children of cst_hole
    compute_time_of("g", "Copying {} to {}".format(6, 7), copy_bst_to_cst, (g, 6))

    # return the game 
    compute_time_of("h", "Pruning the Tree", prune_tree, (g, ))


def prune_tree(g):
    cst = g.tree.root.children[-1]
    g.tree.root.move_tree(cst)


def copy_bst_to_cst(g, bst_index):
    bst = g.tree.root.children[bst_index]
    cst = g.tree.root.children[bst_index+1]
    for branch in xrange(len(cst.children)):
        cst.children[branch].copy_tree(bst)


def copy_cst_to_bst(g, cst_index):
    cst = g.tree.root.children[cst_index]
    bst = g.tree.root.children[cst_index+1]
    bst.children[0].children[0].copy_tree(cst)
    bst.children[1].copy_tree(cst)


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


if __name__ == '__main__':

    # create the game tree and saver objects, solve the game, print the solutions to a file, print the game
    s = compute_time_of(0, "Creating Saver", common.create_saver, ())
    g = compute_time_of(1, "Creating Game", create_game, (sys.argv,))
    compute_time_of(2, "Creating Tree", create_tree, (g,))
    solutions = compute_time_of(3, "Solving Game", common.solve_game, (g,))
    compute_time_of(4, "Printing Solutions", common.print_solutions, (solutions,s)) 
    compute_time_of(5, "Printing Game", common.print_game, (g,s))
