# libraries that are built-in to python
import os, sys, distutils
from time import time, strftime
from distutils import util
from fractions import Fraction
from numbers import Rational
from ConfigParser import ConfigParser
import itertools

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
                 NUMBER_OF_SUITS,
                 NUMBER_OF_ROUNDS,
                 DEBUG):

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
        self.NUMBER_OF_ROUNDS = NUMBER_OF_ROUNDS

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

        # we need to globally keep track of the betting round we're on
        self.deal_sizes    = [self.HAND_SIZE,
                              self.FLOP_SIZE,
                              self.TURN_SIZE,
                              self.RIVER_SIZE]

        # we need to globally keep track of the names, amounts to deal, any 
        # repititions in dealing, and the indexof the branch we're currently
        # looking at
        self.rounds = [Round(name                 = "Hole",  
                             deal_size            = self.HAND_SIZE,  
                             repeat               = 2, 
                             child_index          = 0, 
                             deal_string_template = "{} received ({},{}) and {} received ({},{})."), 
                       Round(name                 = "Flop",  
                             deal_size            = self.FLOP_SIZE, 
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "Flop cards were ({},{},{})."),
                       Round(name                 = "Turn",  
                             deal_size            = self.TURN_SIZE,  
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "Turn card was ({})."),
                       Round(name                 = "River", 
                             deal_size            = self.RIVER_SIZE, 
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "River card was ({}).")]

        # this will hold the card labels that are currently in play
        self.cards_in_play = [None, None, None, None, None, None, None, None, None]

        # testing
        self.DEBUG = DEBUG

        # mappings for Manila Poker
        self.mpm = deuces_wrapper.Manila_Poker_Mapping()

        # variable to keep track of the tree
        self.tree      = None

    def __repr__(self):
        
        # the string to return
        return_str = ""

        return_str += "Decks -- "

        # print out every non-empty list in decks...
        for i in range(len(self.decks)):
            if self.decks[i] == []:
                break
            else:
                return_str += "decks[{}]={}, ".format(i, self.decks[i])

        return_str += "Rounds -- "

        # print out every round...
        for i in range(len(self.rounds)):
            return_str += "rounds[{}]={}, ".format(i, self.rounds[i])

        return_str += "Player 1 -- "

        # print player 1's cards...
        for i in range(0, self.HAND_SIZE):
            return_str += "cards_in_play[{}]={}, ".format(i, self.cards_in_play[i])

        return_str += "Player 2 -- "

        # print player 2's cards...
        for i in range(2, 2*self.HAND_SIZE):
            return_str += "cards_in_play[{}]={}, ".format(i, self.cards_in_play[i])

        return_str += "Board -- "

        # print board's cards...
        for i in range(4, len(self.cards_in_play)):
            return_str += "cards_in_play[{}]={}, ".format(i, self.cards_in_play[i])

        return return_str


class Round(object):

    def __init__(self, name, deal_size, repeat, child_index, deal_string_template):
        self.name                 = name
        self.deal_size            = deal_size
        self.repeat               = repeat
        self.child_index          = child_index
        self.deal_string_template = deal_string_template

    def __repr__(self):
        separator          = ""
        name_str           = "name={name},".format(name = self.name).ljust(12)
        deal_size_str      = "deal_size={deal_size}, ".format(deal_size = self.deal_size)
        repeat_str         = "repeat={repeat}, ".format(repeat = self.repeat)
        child_index_str    = "child_index={child_index}".format(child_index = self.child_index)
        return_str_content = separator.join((name_str, deal_size_str, repeat_str, child_index_str))
        return_str         = "({})".format(return_str_content)

        return return_str


def create_game(cfg):


    # try to get user input
    USAGE_OUTPUT = """
    Usage: python gen_tree_simple [PLAYER_1 (str)
                                   PLAYER_2 (str)
                                   MIXED_STRATEGIES (bool)
                                   ANTE (int > 0)
                                   BET (int > 0)
                                   RAISE (int > 0)
                                   ACE_WRAPS (bool)
                                   LOWEST_CARD (int: 2->13)
                                   HIGHEST_CARD (int: LOWEST_CARD->14)
                                   NUMBER_OF_SUITS (int: 1->4)
                                   NUMBER_OF_ROUNDS (int: 2->4)
                                   DEBUG (bool)]"""

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
            NUMBER_OF_ROUNDS = int(cfg.get(PERSONAL_SECTION,"NUMBER_OF_ROUNDS"))
            DEBUG            = distutils.util.strtobool(cfg.get(TESTING_SECTION,"DEBUG"))

        
        # values added as arguments
        elif len(sys.argv)  == 13:
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
            NUMBER_OF_ROUNDS = int(sys.argv[11])
            DEBUG            = distutils.util.strtobool(sys.argv[12])
        
        # improper amount of values added
        else:    
            raise ValueError
        
        # extra checks
        message = ""
        if ANTE < 0:
            message += "ANTE ({}) cannot be less than 0. ".format(ANTE)
        if BET < 0:
            message += "BET ({}) cannot be less than 0. ".format(BET)
        if RAISE < 0:
            message += "RAISE ({}) cannot be less than 0. ".format(RAISE)
        if LOWEST_CARD < 2:
            message += "LOWEST_CARD ({}) cannot be less than 2. ".format(LOWEST_CARD)
        if LOWEST_CARD > 13:
            message += "LOWEST_CARD ({}) cannot be greater than 13. ".format(LOWEST_CARD)
        if HIGHEST_CARD <= LOWEST_CARD:
            message += "HIGHEST_CARD ({}) cannot be less than or equal to LOWEST_CARD ({}). ".format(HIGHEST_CARD, LOWEST_CARD)
        if HIGHEST_CARD > 14:
            message += "HIGHEST_CARD ({}) cannot be greater than 14. ".format(HIGHEST_CARD)
        if NUMBER_OF_SUITS < 1:
            message += "NUMBER_OF_SUITS ({}) cannot be less than 1. ".format(NUMBER_OF_SUITS)
        if NUMBER_OF_SUITS > 4:
            message += "NUMBER_OF_SUITS ({}) cannot be greater than 4. ".format(NUMBER_OF_SUITS)
        if (HIGHEST_CARD-LOWEST_CARD+1)*NUMBER_OF_SUITS < get_minimum_deck_size(NUMBER_OF_ROUNDS):
            message += "(HIGHEST_CARD-LOWEST_CARD+1)*NUMBER_OF_SUITS ({}) cannot be less than MINIMUM_DECK_SIZE ({}). ".format(
                (HIGHEST_CARD-LOWEST_CARD+1)*NUMBER_OF_SUITS, get_minimum_deck_size(NUMBER_OF_ROUNDS))
        if NUMBER_OF_ROUNDS < 1:
            message += "NUMBER_OF_ROUNDS ({}) cannot be less than 2. ".format(NUMBER_OF_ROUNDS)
        if NUMBER_OF_ROUNDS > 4:
            message += "NUMBER_OF_ROUNDS ({}) cannot be less than 4. ".format(NUMBER_OF_ROUNDS)
        if message != "":
           raise Exception(message)
    
    # stop the script if anything went wrong
    except ValueError():
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
              NUMBER_OF_SUITS=NUMBER_OF_SUITS,
              NUMBER_OF_ROUNDS=NUMBER_OF_ROUNDS,
              DEBUG=DEBUG)
    
    # create the tree, title, and players
    g.tree = gambit.Game.new_tree()
    g.tree.players.add(PLAYER_1)
    g.tree.players.add(PLAYER_2)
    TITLE_FORMAT = "PSP Game with {} players and cards from range {} to {} with {} suits (via tree-method)"
    g.tree.title = TITLE_FORMAT.format(len(g.tree.players), g.LOWEST_CARD, g.HIGHEST_CARD, g.NUMBER_OF_SUITS)

    # create the outcomes
    g.NO_WINNER           = multiply_outcome(g, "No Winner",  0)
    g.PLAYER_1_WINS_SMALL = multiply_outcome(g, "Player 1 Wins Small",  1)
    g.PLAYER_1_WINS_BIG   = multiply_outcome(g, "Player 1 Wins Big",    3)
    g.PLAYER_2_WINS_SMALL = multiply_outcome(g, "Player 2 Wins Small", -1)
    g.PLAYER_2_WINS_BIG   = multiply_outcome(g, "Player 2 Wins Big",   -3)

    # create the cards
    g.decks[0] = create_card_labels(g)

    # # we need to stop the script if they never specified enough cards
    # # MINIMUM_DECK_SIZE = (g.HAND_SIZE * len(g.tree.players)) + g.FLOP_SIZE + g.TURN_SIZE + g.RIVER_SIZE
    # # MINIMUM_DECK_SIZE = ( 2 * 2 ) + 3 + 1 + 1
    # minimum_deck_size = 0
    # for i in range(get_number_of_rounds(g)):
    #     minimum_deck_size += g.rounds[i].deal_size

    # deck_size = g.decks[0]
    # if len(g.decks[0]) < minimum_deck_size:
    #     message = "Deck size ({}) is less than the minimum size allowed ({}), given the number of rounds.".format(
    #         deck_size,
    #         minimum_deck_size)
    #     raise Exception(message)

    # we're done setting up the game
    return g


def create_tree(args):
    
    if g.DEBUG:
        import pudb; pu.db

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
    deck_size = len(g.decks[get_deck_index(deal_size, repeat, bet_round)])

    # compute the amount
    number_of_dealings_iterable = range(repeat+1)

    for number in number_of_dealings_iterable:

        # Calculate the number of card combinations for this round of cards getting flipped
        number_of_deal_combinations *= math_extended.combinations(deck_size, deal_size)

        # adjust the deal_size in case we need have one more dealing
        deck_size -= deal_size

    # create the branches
    iset_chance = root.append_move(g.tree.players.chance, number_of_deal_combinations)

    # label the chance node
    round_name        = get_round(g, bet_round).name
    node_label_suffix = "Chance node for {} Round".format(round_name)
    root.label        = set_node_label(root, bet_round, node_label_suffix, False)
    
    # set the members index to zero
    set_child_index(g, bet_round, 0)

    # populated the branches that were just created
    populate_cst(g, iset_chance, repeat, bet_round, [])


def populate_cst(g, iset_chance, repeat, bet_round, all_cards):

    # get the number of cards we need to deal out
    deal_size = get_deal_size(g, bet_round)

    # we want to keep a backup of all_cards
    temp_all_cards = all_cards[:]

    # get the decks we'll be modifying
    current_deck_index = get_deck_index(deal_size, repeat, bet_round)
    current_deck = get_deck(g, deal_size, repeat, bet_round)
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
            child_index = get_child_index(g, bet_round)

            # we need to label the branch
            deal_string = get_deal_string(g, bet_round, child_index)
            iset_chance.actions[child_index].label = deal_string

            # get the current child itself...
            child = iset_chance.members[0].children[child_index]

            # create the bst for the child node
            create_bst(g, child, iset_chance, deal_size, bet_round)

            # increment member_index since we're done creating this tree branch
            set_child_index(g, bet_round, child_index+1)


        # otherwise, we're in the hole_cards round and we need to repeat one more time to get player 2s cards
        else:
            populate_cst(g, iset_chance, repeat-1, bet_round, all_cards)
        
        # reset the next deck and all_cards to before we messed with them
        next_deck     = []
        all_cards     = temp_all_cards[:]


def create_bst(g, root, iset_bet, deal_size, bet_round):
    
    # Here is the genernal bst
    # Formula: x = 2n-1
    #               A 
    #            /     \
    #         B           B
    #      /  |\        /  \
    #    A    C T     A     C
    #  /  \          / \
    # C   T         C   T

    # player names
    p1 = g.tree.players[0]
    p2 = g.tree.players[1]

    # this will indicate if we should stop creating cst's
    stop = is_last_round(g, bet_round)

    ###############################################
    ########## CREATE ROW 1 AND BRANCHES ##########
    ###############################################

    # we need to create player 1's betting and checking branches
    node = root; player = p1
    action_labels = ["{}. {} bets", "{}. {} checks"]
    node_label_suffix = "{}'s Decision Node".format(player.label)
    create_action_node(node, player, bet_round, action_labels, node_label_suffix)

    ###############################################
    ########## CREATE ROW 2 AND BRANCHES ##########
    ###############################################

    # at the end of player 1's betting branch, 
    #   we need to create player 2's choice node that has raising, calling, and a folding branches
    node = root.children[0]; player = p2
    action_labels = ["{}. {} raises", "{}. {} calls", "{}. {} folds"]
    node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
    create_action_node(node, player, bet_round, action_labels, node_label_suffix)

    # at the end of player 1's betting branch, 
    #   we need to create player 2's choice node that has raising and checking branches
    node = root.children[1]; player = p2
    action_labels = ["{}. {} raises", "{}. {} checks"]
    node_label_suffix = "{}'s Response Node given {} Checks".format(player.label, node.parent.player.label)
    create_action_node(node, player, bet_round, action_labels, node_label_suffix)

    ###############################################
    ########## CREATE ROW 3 AND BRANCHES ##########
    ###############################################

    # at the end of player 2's raising branch, 
    #   we need to create player 1's choice node that has calling and folding branches
    node = root.children[0].children[0]; player = p1
    action_labels = ["{}. {} calls", "{}. {} folds"]
    node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
    create_action_node(node, player, bet_round, action_labels, node_label_suffix)

    # at the end of player 2's calling branch, 
    #   we need to create the chance branch
    node = root.children[0].children[1];
    create_chance_or_terminal_node(node, bet_round, stop)    

    # at the end of player 2's folding branch, 
    #   we need to create the terminal outcome branch
    node = root.children[0].children[2]; player = p1
    node_label_suffix = "{} folds".format(player.label)
    create_terminal_node(node, bet_round, node_label_suffix)  

    # at the end of player 2's raising branch, 
    #   we need to create player 1's choice node that has calling and folding branches
    node = root.children[1].children[0]; player = p1
    action_labels = ["{}. {} calls", "{}. /{} folds"]
    node_label_suffix = "{}'s Response Node given {} Raises".format(player.label, node.parent.player.label)
    create_action_node(node, player, bet_round, action_labels, node_label_suffix)

    # at the end of player 2's raising branch, 
    #   we need to create a cst or terminal node
    node = root.children[1].children[1]
    create_chance_or_terminal_node(node, bet_round, stop)  

    ###############################################
    ########## CREATE ROW 4 AND BRANCHES ##########
    ###############################################

    # at the end of player 1's calling branch, 
    #   we need to create a cst or terminal node
    node = root.children[0].children[0].children[0]
    create_chance_or_terminal_node(node, bet_round, stop) 

    # at the end of player 1's folding branch, 
    #   we need to create a terminal node
    node = root.children[0].children[0].children[1]; player = p1
    node_label_suffix = "{} folds".format(player.label)
    create_terminal_node(node, bet_round, node_label_suffix)  

    # at the end of player 1's calling branch, 
    #   we need to create a cst or terminal node
    node = root.children[1].children[0].children[0]
    create_chance_or_terminal_node(node, bet_round, stop) 

    # at the end of player 1's folding branch, 
    #   we need to create a terminal node
    node = root.children[1].children[0].children[1]; player = p1
    node_label_suffix = "{} folds".format(player.label)
    create_terminal_node(node, bet_round, node_label_suffix)   


def create_terminal_node(node, bet_round, node_label_suffix):
    
    node_label_suffix = "Terminal node. {}".format(node_label_suffix)
    node.label = set_node_label(node, bet_round, node_label_suffix, True)


def create_chance_or_terminal_node(node, bet_round, stop):

    if stop:
        node_label_suffix = "No More Rounds."
        create_terminal_node(node, bet_round, node_label_suffix)
    else:
        create_cst(g, node, 0, bet_round+1)


def create_action_node(node, player, bet_round, action_labels, node_label_suffix):
    n_actions = len(action_labels)
    iset = node.append_move(player, n_actions)
    for i in range(n_actions):
        action_label = action_labels[i]
        iset.actions[i].label = action_label.format(i, player.label)

    # label player's choice node
    node.label = set_node_label(node, bet_round, node_label_suffix, False)


def set_node_label(node, bet_round, NODE_DESCRIPTION, is_terminal):
    '''
    Should return labels of the form: UNIQUE_ID - NODE_DESCRIPTION
    '''

    # if the node is the root node, just return the n
    root = node.game.root

    if node == root:
        UNIQUE_ID = "C"

    # otherwise, we need to create the label by looking at the parent node
    else:
        
        # get child_index for node-labelling purposes
        # child_index = get_child_index(g, bet_round)
        child_index = node.prior_action.label.split(".")[0]

        # get the parent's unique identifier 
        # C0-A0-B - Colin's Response Node given Rose Bet
        # returns: C0-A0-B
        UNIQUE_ID_PARENT = node.parent.label.split()[0]

        # A for Player 1, B for Player 2, C for Chance, T for Terminal
        player = node.player
        if player == g.tree.players[0]:
            player_id = "A"
        elif player == g.tree.players[1]:
            player_id = "B"
        elif player == g.tree.players.chance:
            player_id = "C"
        elif is_terminal:
            player_id = "T"
        else:
            raise Exception("I have no idea what player this is: {}".format(player))
        
        # given C0-A0-B, we might want to create the new id C0-A0-B0-T = UNIQUE_ID_PARENT + 0-T
        UNIQUE_ID = "{}{}-{}".format(UNIQUE_ID_PARENT, child_index, player_id)

    # this is the label we'd like to return
    label = "{} - {}".format(UNIQUE_ID, NODE_DESCRIPTION)

    return label


def get_hole_cards(g):
    hole_cards = [g.cards_in_play[0], g.cards_in_play[1], g.cards_in_play[2], g.cards_in_play[3]]
    return hole_cards


def get_flop_cards(g):
    flop_cards = [g.cards_in_play[4], g.cards_in_play[5], g.cards_in_play[6]]
    return flop_cards


def get_turn_card(g):
    turn_card = [g.cards_in_play[7]]
    return turn_card


def get_river_card(g):
    river_card = [g.cards_in_play[8]]
    return river_card


def get_deal_string(g, bet_round, child_index):

    # we need the chance round for which the cards are being dealt, 
    # and which cards were dealt
    current_round = get_round(g, bet_round)
    template = current_round.deal_string_template
    if bet_round == 1:
        hole_cards = get_hole_cards(g)
        return_str = template.format(g.tree.players[0].label, 
                                     hole_cards[0],
                                     hole_cards[1],
                                     g.tree.players[1].label, 
                                     hole_cards[2],
                                     hole_cards[3])
    elif bet_round == 2:
        flop_cards = get_flop_cards(g)
        return_str = template.format(flop_cards[0],
                                     flop_cards[1],
                                     flop_cards[2])
    elif bet_round == 3:
        turn_card = get_hole_cards(g)
        return_str = template.format(turn_card)
    elif bet_round == 4:
        river_card = get_hole_cards(g)
        return_str = template.format(river_card)
    else:
        raise Exception("Bad bet_round was given: {}".format(bet_round))

    # we also want to prepend the child number to the string
    return_str = "{}. {}".format(child_index, return_str)

    return return_str


def get_minimum_deck_size(n):
    if n == 1:
        return 4
    elif n == 2:
        return 7
    elif n == 3:
        return 8
    elif n == 4:
        return 9
    else:
        raise Exception("Bad value for NUMBER_OF_ROUNDS. Should be from 1 to 4. Given ({})".format(n))


def is_last_round(g, bet_round):
    number_of_rounds = get_number_of_rounds(g)
    last_round = False
    if bet_round == number_of_rounds:
        last_round = True
    elif bet_round > number_of_rounds:
        raise Exception("bet_round ({}) exceeded the maximum number of rounds ({})".format(bet_round, number_of_rounds))
    return last_round


def get_number_of_rounds(g):
    number_of_rounds = g.NUMBER_OF_ROUNDS
    return number_of_rounds


def get_round_index(bet_round):
    if 1 <= bet_round <= 4: 
        round_index = bet_round - 1 
    else:                   
        raise ValueError("Bad value for bet_round ({})".format(bet_round))
    return round_index


def get_round(g, bet_round):
    round_index = get_round_index(bet_round)
    current_round = g.rounds[round_index]
    return current_round


def get_deal_size_index(bet_round):
    deal_size_index = get_round_index(bet_round)
    return deal_size_index


def get_deal_size(g, bet_round):
    deal_size = get_round(g, bet_round).deal_size
    return deal_size


def get_deck_index(deal_size, repeat, bet_round):
    if   deal_size == 2 and repeat == 1 and bet_round == 1: decks_index = 0
    elif deal_size == 2 and repeat == 0 and bet_round == 1: decks_index = 1
    elif deal_size == 3 and repeat == 0 and bet_round == 2: decks_index = 2
    elif deal_size == 1 and repeat == 0 and bet_round == 3: decks_index = 3
    elif deal_size == 1 and repeat == 0 and bet_round == 4: decks_index = 4
    else: raise ValueError("Bad values for deal_size ({}), repeat ({}), and/or bet round ({})".format(deal_size, repeat, bet_round))
    return decks_index


def get_deck(g, deal_size, repeat, bet_round):
    deck_index = get_deck_index(deal_size, repeat, bet_round)
    deck = g.decks[deck_index]
    return deck


def get_child_index_index(bet_round):
    child_index_index = get_round_index(bet_round)
    return child_index_index


def get_child_index(g, bet_round):
    current_round = get_round(g, bet_round)
    child_index = current_round.child_index
    return child_index


def get_children_indices(g):
    
    return_list = []
    for i in range(get_number_of_rounds(g)):
        r = g.rounds[i]
        return_list.append(r.child_index)
    return return_list


def set_child_index(g, bet_round, value):
    current_round = get_round(g, bet_round)
    current_round.child_index = value


def get_cards_in_play_index(deal_size, repeat, bet_round):

    if   deal_size == 2 and repeat == 1 and bet_round == 1: cards_in_play_index = 0
    elif deal_size == 2 and repeat == 0 and bet_round == 1: cards_in_play_index = 2
    elif deal_size == 3 and repeat == 0 and bet_round == 2: cards_in_play_index = 4
    elif deal_size == 1 and repeat == 0 and bet_round == 3: cards_in_play_index = 7
    elif deal_size == 1 and repeat == 0 and bet_round == 4: cards_in_play_index = 8
    else: raise ValueError("Bad values for deal_size ({}), repeat ({}), and/or bet round ({})".format(deal_size, repeat, bet_round))
    return cards_in_play_index


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