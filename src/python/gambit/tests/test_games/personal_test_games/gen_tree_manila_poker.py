# libraries that are built-in to python
import os, sys, distutils
from time import time, strftime
from distutils import util
from fractions import Fraction
from numbers import Rational
from ConfigParser import ConfigParser
import itertools
# import pdb

# libraries from GitHub
import gambit, deuces

# custom libraries
import math_extended
from utils import compute_time_of
import common
import deuces_wrapper


class Poker(gambit.Game):

    def __init__(self, 
                 MIXED_STRATEGIES,
                 ANTE, 
                 BET, 
                 RAISE,
                 ACE_WRAPS,
                 LOWEST_CARD, 
                 HIGHEST_CARD, 
                 NUMBER_OF_SUITS):

        # card values
        self.ACE_WRAPS       = ACE_WRAPS
        self.LOWEST_CARD     = LOWEST_CARD
        self.HIGHEST_CARD    = HIGHEST_CARD
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
        # decks[0] = before any cards are deal
        # decks[1] = after dealing both cards to player 1
        # decks[2] = after dealing both cards to player 2
        # decks[3] = after dealing all flop cards
        # decks[4] = after dealing the turn card
        # decks[5] = after dealing the river card
        self.decks         = [[],[],[],[],[],[]] # there are 6

        # we need to globally keep track of the index we're on for each child
        # members_index[0] = hole children index
        # members_index[0] = flop children index
        # members_index[0] = turn children index
        # members_index[0] = river children index
        self.members_index = [0,0,0,0]
        
        # we need to globally keep track of the betting round we're on
        self.deal_sizes    = [self.HAND_SIZE,
                              self.FLOP_SIZE,
                              self.TURN_SIZE,
                              self.RIVER_SIZE]

        # we need to globally keep track of the name of the round
        self.round_names   = ["Hole",
                              "Flop",
                              "Turn",
                              "River"]

        self.cards_in_play = [None, None, None, None, None, None, None, None, None]

        # testing
        self.DEBUG = True

        # mappings for Manila Poker
        self.mpm = deuces_wrapper.Manila_Poker_Mapping()

        # template subtree holders
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
            TESTING_SECTION  = "testing"
            PLAYER_1         = cfg.get(GAME_SECTION,"PLAYER_1")
            PLAYER_2         = cfg.get(GAME_SECTION,"PLAYER_2")
            MIXED_STRATEGIES = distutils.util.strtobool(cfg.get(GAME_SECTION,"MIXED_STRATEGIES"))
            ANTE             = int(cfg.get(POKER_SECTION,"ANTE"))
            BET              = int(cfg.get(POKER_SECTION,"BET"))
            RAISE            = int(cfg.get(POKER_SECTION,"RAISE"))
            ACE_WRAPS        = distutils.util.strtobool(cfg.get(MANILA_SECTION,"ACE_WRAPS"))
            LOWEST_CARD      = int(cfg.get(MANILA_SECTION,"LOWEST_CARD"))
            HIGHEST_CARD     = int(cfg.get(PERSONAL_SECTION,"HIGHEST_CARD"))
            NUMBER_OF_SUITS  = int(cfg.get(PERSONAL_SECTION,"NUMBER_OF_SUITS"))
            DEBUG            = distutils.util.strtobool(cfg.get(TESTING_SECTION,"DEBUG"))

        
        # values added as arguments
        elif len(sys.argv)  == 12:
            PLAYER_1         = sys.argv[1]
            PLAYER_2         = sys.argv[2]
            MIXED_STRATEGIES = distutils.util.strtobool(sys.argv[3])
            ANTE             = int(sys.argv[4])
            BET              = int(sys.argv[5])
            RAISE            = int(sys.argv[6])
            ACE_WRAPS        = distutils.util.strtobool(sys.argv[7])
            LOWEST_CARD      = int(sys.argv[8])
            HIGHEST_CARD     = int(sys.argv[9])
            NUMBER_OF_SUITS  = int(sys.argv[10])
            DEBUG            = distutils.util.strtobool(sys.argv[11])
        
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
              ACE_WRAPS=ACE_WRAPS,
              LOWEST_CARD=LOWEST_CARD, 
              HIGHEST_CARD=HIGHEST_CARD, 
              NUMBER_OF_SUITS=NUMBER_OF_SUITS)
    
    # create the tree, title, and players
    g.tree = gambit.Game.new_tree()
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

    # testing purposes
    g.DEBUG = DEBUG

    # create the cards
    g.decks[0] = create_card_labels(g)

    # we're done setting up the game
    return g


def create_tree(args):

    print("Beginning to compute payoff tree".format(g.tree.title))

    # we want to start this tree by creating a chance node
    create_cst(g=g, 
               root=g.tree.root,
               repeat=len(g.tree.players)-1, 
               bet_round=1)


def create_cst(g, root, repeat, bet_round):
    """
    g: the game itself
    root: the node for which we'd like to create the cst   
    repeat: the number of times we'll deal the cards
    combinations: the number combinations we have so far
    """

    # we want to hole on to the number of combinations we can deal out
    number_of_deal_combinations = 1
    
    # get the number of cards we need to deal out
    deal_size = get_deal_size(g, bet_round)

    # get the deck size
    deck_size = len(g.decks[get_decks_index(deal_size, repeat, bet_round)])

    for number in range(repeat+1):

        # Calculate the number of card combinations for this round of cards getting flipped
        number_of_deal_combinations *= math_extended.combinations(deck_size, deal_size)

        # adjust the deal_size in case we need have one more dealing
        deck_size -= deal_size

    # label the chance node
    round_name = get_round_name(g, bet_round)
    root.label = "Chance node for {} Round".format(round_name)
    
    # create the branches
    iset_chance = root.append_move(g.tree.players.chance, number_of_deal_combinations)

    # populated the branches that were just created
    g.members_index[get_members_index_index(deal_size, repeat, bet_round)] = 0
    populate_cst(g, iset_chance, repeat, bet_round, [])

def populate_cst(g, iset_chance, repeat, bet_round, all_cards):

    # get the number of cards we need to deal out
    deal_size = get_deal_size(g, bet_round)

    # we want to keep a backup of all_cards
    temp_all_cards = all_cards[:]

    # get the decks we'll be modifying
    current_deck_index = get_decks_index(deal_size, repeat, bet_round)
    current_deck = g.decks[current_deck_index]
    next_deck    = g.decks[current_deck_index+1]
    deck_of_indices = range(len(current_deck))

    # get all possible combinations we want to iterate over
    all_combinations = list(itertools.combinations(deck_of_indices, deal_size))
    for deal in all_combinations:

        # for every combination...
        for i in range(len(deal)):

            # save the current card to cards_in_play
            cards_in_play_index = get_cards_in_play_index(deal_size, repeat, bet_round)
            g.cards_in_play[cards_in_play_index+i] = current_deck[deal[i]]
            all_cards.append(current_deck[deal[i]])

            # copy whatever cards we need to the next deck
            if i == 0:
                next_deck += current_deck[:deal[i]]
            if i == len(deal)-1:
                next_deck += current_deck[deal[i]+1:]
            else:
                next_deck += current_deck[deal[i]+1:deal[i+1]]

        # if we're not repeating, then we can continue to creating the bet branch
        if repeat == 0:

            # get the current child index... 
            member_index_index = get_members_index_index(deal_size, repeat, bet_round)
            
            # get the current child itself...
            child = iset_chance.members[0].children[g.members_index[member_index_index]]

            # if g.DEBUG:
            #     print("append_move passed... member_index_index={}, g.members_index[member_index_index]={}, all_cards={}, current_deck={}"
            #         .format(                 member_index_index,    g.members_index[member_index_index],    all_cards,    current_deck))
            #     raw_input()

            # try:
            #     iset_bet = child.append_move(g.tree.players[0], 2)
            # except Exception:
            #     raise ValueError("append_move failed... member_index_index={}, g.members_index[member_index_index]={}".format(member_index_index, g.members_index[member_index_index]))

            if bet_round == 1: 
                start_time = time()
                print("got here")
            
            create_bst(g, child, iset_chance, deal_size, bet_round)
            
            if bet_round == 1: 
                print("finished tree for member={} in {} seconds").format(str(g.members_index[member_index_index]).ljust(5), time()-start_time)


            # increment member_index since we're done creating this tree branch
            g.members_index[member_index_index] += 1


        # otherwise, we're in the hole_cards round and we need to repeat one more time to get player 2s cards
        else:
            populate_cst(g, iset_chance, repeat-1, bet_round, all_cards)
        
        # reset the next deck and all_cards to before we messed with them
        next_deck     = []
        all_cards     = temp_all_cards[:]

def create_bst(g, root, iset_bet, deal_size, bet_round):
    
    # player names
    p1 = g.tree.players[0].label
    p2 = g.tree.players[1].label

    # create the bst tree template
    root.label = "{}'s' Decision Node".format(p1)

    # we need to create player 1's betting and checking branches
    p1_iset = root.append_move(g.tree.players[0], 2)
    p1_iset.actions[0].label = "{} bets".format(p1)
    p1_iset.actions[1].label = "{} checks".format(p1)

    # at the end of player 1's betting branch, 
    #   we need to create a player 2's choice node that has calling and a folding branches
    root.children[0].label = "{}'s Response Node given {} Bet".format(p2, p1)
    p1_bet_p2_iset = root.children[0].append_move(g.tree.players[1], 2)
    p1_bet_p2_iset.actions[0].label = "{} calls".format(p2)
    p1_bet_p2_iset.actions[1].label = "{} folds".format(p2)

    # at the end of player 1's checking branch, 
    #   we need to create a chance node to continue the game
    # root.children[1].label = "{}'s Response Node given {} Checked".format(p2, p1)
    if not is_last_round(g, bet_round):
        create_cst(g, root.children[1], 0, bet_round+1)
    else:
        root.children[1].label = "Terminal node. No More Rounds."

    # at the end of player 2's calling branch, 
    #   we want to label the node and create a chance node to continue the game
    if not is_last_round(g, bet_round):
        create_cst(g, root.children[0].children[0], 0, bet_round+1)
    else:
        root.children[0].children[0].label = "Terminal node. No More Rounds."
    
    # at the end of player 2's calling branch,
    #   we have a terminal node that 
    root.children[0].children[1].label = "Terminal node. {} folds.".format(p2)

def is_last_round(g, bet_round):
    number_of_rounds = get_number_of_rounds(g)
    last_round = False
    if bet_round == number_of_rounds:
        last_round = True
    elif bet_round > number_of_rounds:
        raise Exception("bet_round ({}) exceeded the maximum number of rounds ({})".format(bet_round, number_of_rounds))
    return last_round

def get_number_of_rounds(g):
    number_of_rounds = len(g.round_names)
    return number_of_rounds

def get_round_name(g, bet_round):
    round_name_index = get_round_name_index(bet_round)
    round_name = g.round_names[round_name_index]
    return round_name

def get_round_name_index(bet_round):
    round_name_index = get_deal_size_index(bet_round)
    return round_name_index

def get_deal_size(g, bet_round):
    deal_size_index = get_deal_size_index(bet_round)
    deal_size = g.deal_sizes[deal_size_index]
    return deal_size

def get_deal_size_index(bet_round):
    deal_size_index = bet_round - 1
    return deal_size_index

def get_decks_index(deal_size, repeat, bet_round):
    if   deal_size == 2 and repeat == 1 and bet_round == 1: decks_index = 0
    elif deal_size == 2 and repeat == 0 and bet_round == 1: decks_index = 1
    elif deal_size == 3 and repeat == 0 and bet_round == 2: decks_index = 2
    elif deal_size == 1 and repeat == 0 and bet_round == 3: decks_index = 3
    elif deal_size == 1 and repeat == 0 and bet_round == 4: decks_index = 4
    else: raise ValueError("Bad values for deal_size ({}), repeat ({}), and/or bet round ({})".format(deal_size, repeat, bet_round))
    return decks_index

def get_members_index_index(deal_size, repeat, bet_round):
    decks_index = get_decks_index(deal_size, repeat, bet_round)
    if        decks_index == 0: members_index_index = 0
    elif 1 <= decks_index <= 4: members_index_index = decks_index - 1
    return members_index_index

def get_cards_in_play_index(deal_size, repeat, bet_round):

    if   deal_size == 2 and repeat == 1 and bet_round == 1: cards_in_play_index = 0
    elif deal_size == 2 and repeat == 0 and bet_round == 1: cards_in_play_index = 2
    elif deal_size == 3 and repeat == 0 and bet_round == 2: cards_in_play_index = 4
    elif deal_size == 1 and repeat == 0 and bet_round == 3: cards_in_play_index = 7
    elif deal_size == 1 and repeat == 0 and bet_round == 4: cards_in_play_index = 8
    else: raise ValueError("Bad values for deal_size ({}), repeat ({}), and/or bet round ({})".format(deal_size, repeat, bet_round))
    return cards_in_play_index

def handle_flop(g, i, p1_bet):
    
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
    for index_card5 in range(len(g.deck_h2)-2):
        for index_card6 in range(index_card5+1, len(g.deck_h2)-1):
            for index_card7 in range(index_card6+1, len(g.deck_h2)):
                g.cards_in_play[4] = g.deck_h2[index_card5]
                g.cards_in_play[5] = g.deck_h2[index_card6]
                g.cards_in_play[6] = g.deck_h2[index_card7]
                g.deck_f = g.deck_h2[:index_card5] +              \
                           g.deck_h2[index_card5+1:index_card6] + \
                           g.deck_h2[index_card6+1:index_card7] + \
                           g.deck_h2[index_card7+1:]

                # ... we need to create a branch for that chance action. 
                j += 1
                iset_round2_label = "{}, {}, {}".format(g.cards_in_play[4], g.cards_in_play[5], g.cards_in_play[6])
                iset.actions[j].label = iset_round2_label

                # calculate payoffs
                if p1_bet:
                    child = g.tree.root.children[i].children[0].children[0].children[j]
                else:
                    child = g.tree.root.children[i].children[1].children[0].children[j]
                winner = deuces_wrapper.return_winner(g)
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


if __name__ == '__main__':

    # create the game tree and saver objects, solve the game, print the solutions to a file, print the game
    s = compute_time_of(0, "Creating Saver", common.create_saver, ())
    g = compute_time_of(1, "Creating Game", create_game, (sys.argv,))
    try:
       compute_time_of(2, "Creating Tree", create_tree, (g,))
        # solutions = compute_time_of(3, "Solving Game", common.solve_game, (g,))
        # compute_time_of(4, "Printing Solutions", common.print_solutions, (solutions,s)) 
    except KeyboardInterrupt:
        pass
    compute_time_of(5, "Printing Game", common.print_game, (g,s))