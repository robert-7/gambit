# libraries that are built-in to python
import os, sys, distutils
from time import time, strftime
from distutils    import util
from fractions    import Fraction
from numbers      import Rational
from ConfigParser import ConfigParser
from ast          import literal_eval
import itertools

# libraries from GitHub
import gambit, deuces

# custom libraries
import math_extended as math
from utils import compute_time_of
import common
import deuces_wrapper as dw


class Identifiers(object):
    '''
    These are strings that will identify which characters performed which 
    actions at a specific moments. This is primarily seen in the output file.
    '''

    def __init__(self):

        # actions and characters
        self.BET       = "B"
        self.CALL      = "K"
        self.CHANCE    = "Z"
        self.CHECK     = "C"
        self.FOLD      = "F"
        self.NO_ACTION = ""
        self.PLAYER1   = "X"
        self.PLAYER2   = "Y"
        self.RAISE     = "R"
        self.RERAISE   = "S"
        self.TERMINAL  = "T"


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
                 DEBUG,
                 SPECIFIC_HOLE=[],
                 SPECIFIC_ACTIONS1=[],
                 SPECIFIC_FLOP=[],
                 SPECIFIC_ACTIONS2=[],
                 SPECIFIC_TURN=[],
                 SPECIFIC_ACTIONS3=[],
                 SPECIFIC_RIVER=[],
                 SPECIFIC_ACTIONS4=[]):

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

        # this will hold the cards that are currently being considered in the game
        # decks[0] = before any cards are deal
        # decks[1] = after dealing both cards to player 1
        # decks[2] = after dealing both cards to player 2
        # decks[3] = after dealing all flop cards
        # decks[4] = after dealing the turn card
        # decks[5] = after dealing the river card
        self.decks             = [[],[],[],[],[],[]] # there are 6
        self.decks[0]          = self.create_card_labels()
        self.cards_to_ints_map = self.create_card_to_ints_map()

        # we need to globally keep track of the betting round we're on
        self.deal_sizes    = [self.HAND_SIZE,
                              self.FLOP_SIZE,
                              self.TURN_SIZE,
                              self.RIVER_SIZE]

        # this will hold the card labels that are currently in play
        self.cards_in_play = [None, None, None, None, None, None, None, None, None]

        # we need to globally keep track of the names, amounts to deal, any 
        # repititions in dealing, and the indexof the branch we're currently
        # looking at
        self.rounds = [Round(name                 = "Hole",  
                             deal_size            = self.HAND_SIZE,  
                             repeat               = 2, 
                             child_index          = 0, 
                             deal_string_template = "{} received ({},{}) and {} received ({},{}).",
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS1), 
                       Round(name                 = "Flop",  
                             deal_size            = self.FLOP_SIZE, 
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "Flop cards were ({},{},{}).",
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS2), 
                       Round(name                 = "Turn",  
                             deal_size            = self.TURN_SIZE,  
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "Turn card was ({}).",
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS3), 
                       Round(name                 = "River", 
                             deal_size            = self.RIVER_SIZE, 
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "River card was ({}).",
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS4)]

        # testing purposes
        self.DEBUG = DEBUG

        # we also want to
        self.set_debug_child_index(SPECIFIC_HOLE, SPECIFIC_FLOP, SPECIFIC_TURN, SPECIFIC_RIVER)

        # mappings for Manila Poker
        self.mpm = dw.Manila_Poker_Mapping()

        # variable to keep track of the tree
        self.tree = None

        # actions and players identifiers
        self.ids = Identifiers()

        # get a list of all possible paths
        self.action_round_paths = [
            (),
            (self.ids.BET,),
            (self.ids.CHECK,),
            (self.ids.BET,   self.ids.RAISE),
            (self.ids.BET,   self.ids.CALL),
            (self.ids.BET,   self.ids.FOLD),
            (self.ids.CHECK, self.ids.BET),
            (self.ids.CHECK, self.ids.CHECK),
            (self.ids.BET,   self.ids.RAISE, self.ids.CALL),
            (self.ids.BET,   self.ids.RAISE, self.ids.FOLD),
            (self.ids.CHECK, self.ids.BET,   self.ids.CALL),
            (self.ids.CHECK, self.ids.BET,   self.ids.FOLD)
        ]

        # the mapping from actions to their respective indices in the tree
        self.atim = {
            self.action_round_paths[0]  : [],
            self.action_round_paths[1]  : [0],
            self.action_round_paths[2]  : [1],
            self.action_round_paths[3]  : [0, 0],
            self.action_round_paths[4]  : [0, 1],
            self.action_round_paths[5]  : [0, 2],
            self.action_round_paths[6]  : [1, 0],
            self.action_round_paths[7]  : [1, 1],
            self.action_round_paths[8]  : [0, 0, 0],
            self.action_round_paths[9]  : [0, 0, 1],
            self.action_round_paths[10] : [1, 0, 0],
            self.action_round_paths[11] : [1, 0, 1]
        }


    def set_debug_child_index(self, HOLE, FLOP, TURN, RIVER):
        '''
        We'd like to represent the node as [int, int, int, int] where 
        each int is supposed to represent the child index. 
        '''

        # combine the cards to create
        cards = HOLE + FLOP + TURN + RIVER

        # if no cards need to be filtered, we can just return
        if cards is None or len(cards) == 0:
            return

        # get the number of cards in the deck
        MAX = (self.HIGHEST_CARD - self.LOWEST_CARD + 1) * self.NUMBER_OF_SUITS

        # identify any bad cards and retrieve the indices for each card
        card_ints = []
        bad_cards = []
        for card in cards:
            if card in self.cards_to_ints_map:
                card_int = self.cards_to_ints_map[card]
                card_ints.append(card_int)
            else:
                bad_cards.append(card)
        
        # if we found a bad card, raise an exception...
        if bad_cards != []:
            if len(bad_cards) == 1:
                error_msg = "Bad card given: {}"
            else:
                error_msg = "Bad cards given: {}"
            separator = ", "
            raise Exception(error_msg.format(separator.join(bad_cards)))

        # get the indices and assign them to rounds 
        child_indices = get_order_chooser(card_ints, MAX)
        for i in range(len(child_indices)):
            self.rounds[i].debug_child_index = child_indices[i]
        
        return child_indices


    def create_card_labels(self):
        '''
        Takes the cards ranks and suits we're interested in and creates card labels from them.
        Example: 
        CARD_RANKS  = ['Q', 'K', 'A']
        CARD_SUITS  = ['s','c','d','h']
        CARD_LABELS = ['Qs', 'Qc', 'Qd', 'Qh', 'Ks', 'Kc', 'Kd', 'Kh', 'As', 'Ac', 'Ad', 'Ah']
        '''

        from itertools import product

        # get the card ranks
        CARD_RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        CARD_RANKS_IN_THIS_GAME = CARD_RANKS[self.LOWEST_CARD-2 : self.HIGHEST_CARD-1]
        
        # get the card suits
        CARD_SUITS = ['s','c','d','h']
        CARD_SUITS_IN_THIS_GAME = CARD_SUITS[ -self.NUMBER_OF_SUITS + 4:]
        
        # create the labels
        SEPARATOR = ""
        CARD_LABELS = [SEPARATOR.join(map(str,card_rank_suit_tuple)) for card_rank_suit_tuple in product(CARD_RANKS_IN_THIS_GAME, CARD_SUITS_IN_THIS_GAME)]
        
        return CARD_LABELS


    def create_card_to_ints_map(self):
        '''
        We'd like to return a reverse mapping for our deck of cards. 
        Example: 
        Given deck = ["Ks", "Kc", "Kd", "Kh", "As", "Ac", "Ad", "Ah"]
        Return:
        { "Ks" : 0, "Kc" : 1, "Kd" : 2, "Kh" : 3, "As" : 4, "Ac" : 5, "Ad" : 6, "Ah" : 7 }
        '''

        # get the deck
        deck = self.decks[0]
        
        # create the mapping
        mapping = {}

        # for every card...
        for card in range(len(deck)):
            
            # add it to the mapping
            mapping[deck[card]] = card

        return mapping


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


    def get_hole_cards(self):
        hole_cards = [self.cards_in_play[0], self.cards_in_play[1], self.cards_in_play[2], self.cards_in_play[3]]
        return hole_cards


    def get_flop_cards(self):
        flop_cards = [self.cards_in_play[4], self.cards_in_play[5], self.cards_in_play[6]]
        return flop_cards


    def get_turn_card(self):
        turn_card = [self.cards_in_play[7]]
        return turn_card


    def get_river_card(self):
        river_card = [self.cards_in_play[8]]
        return river_card


    def get_outcome(self, winner, amount):
        '''
        The amount won is always the loser's contribution to the pot.
        If player 1 is the winner, the index of the outcome is: 
          index = amount - 1
        If player 2 is the winner, the index of the outcome is:
          index = amount
        '''

        # get the index
        index = 0

        # if there is no winner
        if winner is None:
            index = 0
        
        # there is a winner...
        else: 

            # if we gave a bad winner
            if winner not in self.tree.players:
                error_msg = "Our winner is not a player, nor is it None. winner: {}"
                raise Exception(error_msg.format(winner))

            # if amount is not an int...
            if type(amount) is not int:
                error_msg = "amount is not of type int. type(amount): {}"
                raise Exception(error_msg.format(type(amount)))

            # if amount is not a valid int...
            if amount < 0 or amount > 24: 
                error_msg = "amount is not within range of [0, 24]. amount: {}"
                raise Exception(error_msg.format(amount))

            # if player 1 won...
            if winner == self.tree.players[0]:
                index = amount - 1

            # if player 2 won...
            elif winner == self.tree.players[1]:
                index = amount
        
        # get the outcome
        outcome = self.tree.outcomes[index]

        return outcome


    def get_number_of_rounds(g):
        number_of_rounds = g.NUMBER_OF_ROUNDS
        return number_of_rounds


class Round(object):

    def __init__(self, name, deal_size, repeat, child_index, deal_string_template, debug_child_index, debug_actions):
        self.name                 = name
        self.deal_size            = deal_size
        self.repeat               = repeat
        self.child_index          = child_index
        self.deal_string_template = deal_string_template
        self.debug_child_index    = debug_child_index
        self.debug_actions        = debug_actions

    def __repr__(self):
        separator          = ""
        name_str           = "name={name},".format(name = self.name).ljust(12)
        deal_size_str      = "deal_size={deal_size}, ".format(deal_size = self.deal_size)
        repeat_str         = "repeat={repeat}, ".format(repeat = self.repeat)
        child_index_str    = "child_index={child_index}".format(child_index = self.child_index)
        debug_actions      = "debug_actions={debug_actions}".format(debug_actions = self.debug_actions)
        return_str_content = separator.join((name_str, deal_size_str, repeat_str, child_index_str, debug_actions))
        return_str         = "({})".format(return_str_content)

        return return_str


def create_game(cfg):

    def add_outcome_player_1_wins(g, amount):
        '''
        A child function that calls add_outcome given player 1 is the winner.
        '''
        
        add_outcome(g, g.tree.players[0],  amount)


    def add_outcome_player_2_wins(g, amount):
        '''
        A child function that calls add_outcome given player 2 is the winner.
        '''

        add_outcome(g, g.tree.players[1], -amount)


    def add_outcome(g, winner, multiple):
        '''
        Takes the default outcome and multiplies it based on the bet value.
        '''

        outcome_string_template = "{} wins {}"
        outcome_string = outcome_string_template.format(winner.label, abs(multiple))
        new_outcome = g.tree.outcomes.add(outcome_string)
        new_outcome[0] =  multiple
        new_outcome[1] = -multiple
        return new_outcome


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
                                   DEBUG (bool)
                                   NODE (list or None)]"""

    try:
        
        if len(sys.argv)    == 1:

            # create the configuration parser
            CONFIGURATION_FILE = "config.ini"
            cfg = ConfigParser()
            cfg.read(CONFIGURATION_FILE)

            GAME_SECTION      = "game"
            POKER_SECTION     = "poker"
            MANILA_SECTION    = "manila"
            PERSONAL_SECTION  = "personal"
            TESTING_SECTION   = "testing"
            PLAYER_1          = cfg.get(GAME_SECTION,"PLAYER_1")
            PLAYER_2          = cfg.get(GAME_SECTION,"PLAYER_2")
            MIXED_STRATEGIES  = distutils.util.strtobool(cfg.get(GAME_SECTION,"MIXED_STRATEGIES"))
            ANTE              = int(cfg.get(POKER_SECTION,"ANTE"))
            BET               = int(cfg.get(POKER_SECTION,"BET"))
            RAISE             = int(cfg.get(POKER_SECTION,"RAISE"))
            ACE_WRAPS         = distutils.util.strtobool(cfg.get(MANILA_SECTION,"ACE_WRAPS"))
            LOWEST_CARD       = int(cfg.get(MANILA_SECTION,"LOWEST_CARD"))
            HIGHEST_CARD      = int(cfg.get(PERSONAL_SECTION,"HIGHEST_CARD"))
            NUMBER_OF_SUITS   = int(cfg.get(PERSONAL_SECTION,"NUMBER_OF_SUITS"))
            NUMBER_OF_ROUNDS  = int(cfg.get(PERSONAL_SECTION,"NUMBER_OF_ROUNDS"))
            DEBUG             = distutils.util.strtobool(cfg.get(TESTING_SECTION,"DEBUG"))
            SPECIFIC_HOLE     = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_HOLE"))
            SPECIFIC_ACTIONS1 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS1"))
            SPECIFIC_FLOP     = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_FLOP"))
            SPECIFIC_ACTIONS2 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS2"))
            SPECIFIC_TURN     = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_TURN"))
            SPECIFIC_ACTIONS3 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS3"))
            SPECIFIC_RIVER    = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_RIVER"))
            SPECIFIC_ACTIONS4 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS4"))

        
        # values added as arguments
        elif len(sys.argv)  == 14:
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
            NODE             = literal_eval(sys.argv[13])
        
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

    # if we want to debug our code, this is where we do it
    if DEBUG:
        import pudb; pu.db

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
              DEBUG=DEBUG,
              SPECIFIC_HOLE=SPECIFIC_HOLE,
              SPECIFIC_ACTIONS1=SPECIFIC_ACTIONS1,
              SPECIFIC_FLOP=SPECIFIC_FLOP,
              SPECIFIC_ACTIONS2=SPECIFIC_ACTIONS2,
              SPECIFIC_TURN=SPECIFIC_TURN,
              SPECIFIC_ACTIONS3=SPECIFIC_ACTIONS3,
              SPECIFIC_RIVER=SPECIFIC_RIVER,
              SPECIFIC_ACTIONS4=SPECIFIC_ACTIONS4)
    
    # create the tree, title, and players
    g.tree = gambit.Game.new_tree()
    g.tree.players.add(PLAYER_1)
    g.tree.players.add(PLAYER_2)
    TITLE_FORMAT = "PSP Game with {} players and cards from range {} to {} with {} suits (via tree-method)"
    g.tree.title = TITLE_FORMAT.format(len(g.tree.players), g.LOWEST_CARD, g.HIGHEST_CARD, g.NUMBER_OF_SUITS)

    # create the outcomes
    g.tree.outcomes.add("Tie Game")  # g.tree.outcomes[0]  = (  0,  0)
    g.tree.outcomes[0][0] = 0 
    g.tree.outcomes[0][1] = 0          
    add_outcome_player_1_wins(g,  2) # g.tree.outcomes[1]  = (  2, -2)
    add_outcome_player_2_wins(g,  2) # g.tree.outcomes[2]  = ( -2,  2)
    add_outcome_player_1_wins(g,  4) # g.tree.outcomes[3]  = (  4, -4)
    add_outcome_player_2_wins(g,  4) # g.tree.outcomes[4]  = ( -4,  4)
    add_outcome_player_1_wins(g,  6) # g.tree.outcomes[5]  = (  6, -6)
    add_outcome_player_2_wins(g,  6) # g.tree.outcomes[6]  = ( -6,  6)
    add_outcome_player_1_wins(g,  8) # g.tree.outcomes[7]  = (  8, -8)
    add_outcome_player_2_wins(g,  8) # g.tree.outcomes[8]  = ( -8,  8)
    add_outcome_player_1_wins(g, 10) # g.tree.outcomes[9]  = ( 10,-10)
    add_outcome_player_2_wins(g, 10) # g.tree.outcomes[10] = (-10, 10)
    add_outcome_player_1_wins(g, 12) # g.tree.outcomes[11] = ( 12,-12)
    add_outcome_player_2_wins(g, 12) # g.tree.outcomes[12] = (-12, 12)
    add_outcome_player_1_wins(g, 14) # g.tree.outcomes[13] = ( 14,-14)
    add_outcome_player_2_wins(g, 14) # g.tree.outcomes[14] = (-14, 14)
    add_outcome_player_1_wins(g, 16) # g.tree.outcomes[15] = ( 16,-16)
    add_outcome_player_2_wins(g, 16) # g.tree.outcomes[16] = (-16, 16)
    add_outcome_player_1_wins(g, 18) # g.tree.outcomes[17] = ( 18,-18)
    add_outcome_player_2_wins(g, 18) # g.tree.outcomes[18] = (-18, 18)
    add_outcome_player_1_wins(g, 20) # g.tree.outcomes[19] = ( 20,-20)
    add_outcome_player_2_wins(g, 20) # g.tree.outcomes[20] = (-20, 20)
    add_outcome_player_1_wins(g, 22) # g.tree.outcomes[21] = ( 22,-22)
    add_outcome_player_2_wins(g, 22) # g.tree.outcomes[22] = (-22, 22)
    add_outcome_player_1_wins(g, 24) # g.tree.outcomes[23] = ( 24,-24)
    add_outcome_player_2_wins(g, 24) # g.tree.outcomes[24] = (-24, 24)


    # we're done setting up the game
    return g


def specific_node():
    '''
    We'd like to know if we're only creating the tree for a specific node.
    '''

    # for the time-being, we'll always return True
    return True


def prune_tree():
    '''
    We want to set the specific node to be the whole tree.
    '''

    # the list containing all the indices
    children_indices = []

    # for every round...
    for rnd in range(g.get_number_of_rounds()):

        # append the chance child index
        chance_index = g.rounds[rnd].debug_child_index
        if chance_index is not None:
            children_indices.append(chance_index)

        # append the actions list converted to indices
        actions = tuple(g.rounds[rnd].debug_actions)
        if actions not in g.atim:
            raise Exception("actions ({}) is not in our mapping".format(actions))
        action_indices = g.atim[actions]
        children_indices += action_indices

    # get the current node
    node = g.tree.root

    # we need to keep going down the tree until we reach the node in which 
    # we're interested
    for child_index in children_indices:
        node = node.children[child_index]

    # we need to keep replacing the node with its parent node until our node 
    # is the root
    while node.parent is not None:
        node.delete_parent()

    # set the node
    # g.tree.root.move_tree(node)
    node.move_tree(g.tree.root)


def create_tree(args):

    print("Beginning to compute payoff tree".format(g.tree.title))

    # we want to start this tree by creating a chance node
    create_cst(g=g, 
               root=g.tree.root,
               repeat=len(g.tree.players)-1, 
               bet_round=1,
               pot=0)

    # if we're interested in the subtree at a specific node...
    if specific_node():

        # prune the tree to end up with only that node's subtree
        prune_tree()


def create_cst(g, root, repeat, bet_round, pot, action=""):
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
    deck_index = get_deck_index(deal_size, repeat, bet_round)
    deck_size = len(g.decks[deck_index])

    # compute the amount
    number_of_dealings_iterable = range(repeat+1)

    for number in number_of_dealings_iterable:

        # Calculate the number of card combinations for this round of cards getting flipped
        number_of_deal_combinations *= math.combinations(deck_size, deal_size)

        # adjust the deal_size in case we need have one more dealing
        deck_size -= deal_size

    # create the branches
    iset_chance = root.append_move(g.tree.players.chance, number_of_deal_combinations)

    # label the chance node
    round_name        = get_round(g, bet_round).name
    node_label_suffix = "Chance node for {} Round".format(round_name)
    bets              = (pot/2, pot/2)
    root.label        = set_node_label(root, bet_round, node_label_suffix, False, action, bets)
    
    # set the members index to zero
    set_child_index(g, bet_round, 0)

    # populated the branches that were just created
    populate_cst(g, iset_chance, repeat, bet_round, pot, [])


def populate_cst(g, iset_chance, repeat, bet_round, pot, all_cards):

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

            # check if we added a bad card to the list
            # test = g.cards_in_play[:cards_in_play_index+i+1]
            # if len(test) > len(set(test)):
            #     raise Exception()

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

            # create the node only if we're not in debug mode and we specified
            # to create the node, or if we're creating all nodes
            debug_child_index = get_round(g, bet_round).debug_child_index
            if debug_child_index is None or debug_child_index == child_index:

                # get the current child itself...
                child = iset_chance.members[0].children[child_index]

                # create the bst for the child node
                create_bst(g, child, iset_chance, deal_size, bet_round, pot)

            # increment member_index since we're done creating this tree branch
            set_child_index(g, bet_round, child_index+1)

            # reset the g.cards_in_play
            if bet_round <= 4:
                g.cards_in_play[8] = None
                if bet_round <= 3:
                    g.cards_in_play[7] = None
                    if bet_round <= 2:
                        g.cards_in_play[6] = None
                        g.cards_in_play[5] = None
                        g.cards_in_play[4] = None
                        if deal_size == 2:
                            g.cards_in_play[3] = None
                            g.cards_in_play[2] = None


        # otherwise, we're in the hole_cards round and we need to repeat one more time to get player 2s cards
        else:
            populate_cst(g, iset_chance, repeat-1, bet_round, pot, all_cards)

        
        # reset the next deck and all_cards to before we messed with them
        g.decks[current_deck_index+1] = []
        next_deck = g.decks[current_deck_index+1]
        all_cards = temp_all_cards[:]


def create_bst(g, root, iset_bet, deal_size, bet_round, pot):
    
    # Here is the genernal bst
    # Formula: x = 2n-1
    #               A 
    #            /     \
    #         B           B
    #      /  |\        /  \
    #    A    C T     A     C
    #  /  \          / \
    # C   T         C   T

    # get specific actions for this round
    current_round = get_round(g, bet_round)
    specific_actions = current_round.debug_actions

    # player names
    p1 = g.tree.players[0]
    p2 = g.tree.players[1]

    # this will indicate if we should stop creating cst's
    stop = is_last_round(g, bet_round)

    # we can and should calculate the winner first to avoid repetition
    if bet_round != 1:
        winner = get_winner(g, bet_round)
    else:
        winner = None

    ###############################################
    ########## CREATE ROW 1 AND BRANCHES ##########
    ###############################################

    # we need to create player 1's betting and checking branches
    action = g.ids.NO_ACTION
    node = root
    player = p1
    action_labels = ["{}. {} bets", "{}. {} checks"]
    node_label_suffix = "{}'s Decision Node".format(player.label)
    create_action_node(node, player, bet_round, action_labels, node_label_suffix, action)

    ###############################################
    ########## CREATE ROW 2 AND BRANCHES ##########
    ###############################################

    # we are interested in just the first action, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:1]:
        specific_actions_so_far += specific_action

    # at the end of player 1's betting branch, 
    #   we need to create player 2's choice node that has raising, calling, and a folding branches
    actions_so_far = ''.join(g.action_round_paths[1])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[0]
        player = p2
        action_labels = ["{}. {} raises", "{}. {} calls", "{}. {} folds"]
        node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
        create_action_node(node, player, bet_round, action_labels, node_label_suffix, action)

    # at the end of player 1's checking branch, 
    #   we need to create player 2's choice node that has raising and checking branches
    actions_so_far = ''.join(g.action_round_paths[2])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[1]
        player = p2
        action_labels = ["{}. {} bets", "{}. {} checks"]
        node_label_suffix = "{}'s Response Node given {} Checks".format(player.label, node.parent.player.label)
        create_action_node(node, player, bet_round, action_labels, node_label_suffix, action)

    ###############################################
    ########## CREATE ROW 3 AND BRANCHES ##########
    ###############################################

    # we are interested in just the first two actions, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:2]:
        specific_actions_so_far += specific_action

    # at the end of player 2's raising branch, 
    #   we need to create player 1's choice node that has calling and folding branches
    actions_so_far = ''.join(g.action_round_paths[3])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[0].children[0]
        player = p1
        action_labels = ["{}. {} calls", "{}. {} folds"]
        node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
        create_action_node(node, player, bet_round, action_labels, node_label_suffix, action)

    # at the end of player 2's calling branch, 
    #   we need to create the chance branch
    actions_so_far = ''.join(g.action_round_paths[4])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[0].children[1]
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 1*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(node, bet_round, stop, action, winner, bets)    

    # at the end of player 2's folding branch, 
    #   we need to create the terminal outcome branch
    actions_so_far = ''.join(g.action_round_paths[5])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[0].children[2]
        player = p1
        node_label_suffix = "{} folds".format(player.label)
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 0*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_terminal_node(node, bet_round, node_label_suffix, action, winner, bets)  

    # at the end of player 2's betting branch, 
    #   we need to create player 1's choice node that has calling and folding branches
    actions_so_far = ''.join(g.action_round_paths[6])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[1].children[0]
        player = p1
        action_labels = ["{}. {} calls", "{}. {} folds"]
        node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
        create_action_node(node, player, bet_round, action_labels, node_label_suffix, action)

    # at the end of player 2's checking branch, 
    #   we need to create a cst or terminal node
    actions_so_far = ''.join(g.action_round_paths[7])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[1].children[1]
        # bets = get_bets(pot/2 + 0*g.BET, pot/2 + 0*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(node, bet_round, stop, action, winner, bets)

    ###############################################
    ########## CREATE ROW 4 AND BRANCHES ##########
    ###############################################

    # we are interested in all three actions, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:]:
        specific_actions_so_far += specific_action

    # at the end of player 1's calling branch, 
    #   we need to create a cst or terminal node
    actions_so_far = ''.join(g.action_round_paths[8])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[0].children[0].children[0]
        # bets = get_bets(pot/2 + 2*g.BET, pot/2 + 2*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(node, bet_round, stop, action, winner, bets) 

    # at the end of player 1's folding branch, 
    #   we need to create a terminal node
    actions_so_far = ''.join(g.action_round_paths[9])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[0].children[0].children[1]
        player = p1
        node_label_suffix = "{} folds".format(player.label)
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 2*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_terminal_node(node, bet_round, node_label_suffix, action, winner, bets)  

    # at the end of player 1's calling branch, 
    #   we need to create a cst or terminal node
    actions_so_far = ''.join(g.action_round_paths[10])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[1].children[0].children[0]
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 1*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(node, bet_round, stop, action, winner, bets) 

    # at the end of player 1's folding branch, 
    #   we need to create a terminal node
    actions_so_far = ''.join(g.action_round_paths[11])
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = root.children[1].children[0].children[1]
        player = p1
        node_label_suffix = "{} folds".format(player.label)
        # bets = get_bets(pot/2 + 0*g.BET, pot/2 + 1*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_terminal_node(node, bet_round, node_label_suffix, action, winner, bets)   


def get_bets(g, pot, actions_so_far, bet_round):
    '''
    We want to return the values player 1 and player 2 have put into the pot by now.
    '''

    # the tuple we'd like to return
    bets = [pot/2, pot/2]

    # if we're in the turn or river round, we need to double the bet value
    b = g.BET
    r = g.RAISE
    if is_turn_round(g, bet_round) or is_river_round(g, bet_round):
        b *= 2
        r *= 2

    for action_index in range(len(actions_so_far)):
        action = actions_so_far[action_index]
        if action == g.ids.BET:
            bets[action_index % 2] += b
        elif action == g.ids.CALL:
            bets[action_index % 2] = bets[(action_index+1) % 2]
        elif action == g.ids.CHECK:
            pass
        elif action == g.ids.FOLD:
            pass
        elif action == g.ids.RAISE:
            bets[action_index % 2] = bets[(action_index+1) % 2]
            bets[action_index % 2] += b
        else:
            error_msg = "I don't know what action this is ({}) given these actions ({})"
            raise Exception(error_msg.format(action, actions_so_far))

    return tuple(bets)


def create_terminal_node(node, bet_round, node_label_suffix, action, winner, bets):
    
    node_label_suffix = "Terminal node. {}".format(node_label_suffix)
    node.label = set_node_label(node, bet_round, node_label_suffix, True, action, winner, bets)


def create_chance_or_terminal_node(node, bet_round, stop, action, winner, bets):

    if stop:
        node_label_suffix = "No More Rounds."
        create_terminal_node(node, bet_round, node_label_suffix, action, winner, bets)
    else:
        pot = bets[0] + bets[1]
        create_cst(g, node, 0, bet_round+1, pot, action)


def create_action_node(node, player, bet_round, action_labels, node_label_suffix, action):
    n_actions = len(action_labels)
    iset = node.append_move(player, n_actions)
    for i in range(n_actions):
        action_label = action_labels[i]
        iset.actions[i].label = action_label.format(i, player.label)

    # label player's choice node
    node.label = set_node_label(node, bet_round, node_label_suffix, False, action)


def set_node_label_chance(node, bet_round, pot, NODE_DESCRIPTION, is_terminal):
    '''
    This function just calls set_node_label, but with the action being empty.
    '''

    return set_node_label(node, bet_round, (pot/2,pot/2), NODE_DESCRIPTION, is_terminal, NO_ACTION)


def set_node_label(node, bet_round, NODE_DESCRIPTION, is_terminal, action, winner=None, bets=(0,0)):
    '''
    Should return labels of the form: UNIQUE_ID - NODE_DESCRIPTION
    '''

    # if the node is the root node, just return the n
    root = g.tree.root

    if node == root:
        UNIQUE_ID = g.ids.CHANCE

    # otherwise, we need to create the label by looking at the parent node
    else:
        
        # get child_index for node-labelling purposes
        child_index = node.prior_action.label.split(".")[0]

        # get the parent's unique identifier 
        # C0-A0-B - Colin's Response Node given Rose Bet
        # returns: C0-A0-B
        UNIQUE_ID_PARENT = node.parent.label.split()[0]

        # A for Player 1, B for Player 2, C for Chance, T for Terminal
        player = node.player

        # we need to check if this is a terminal node
        # if player is None:
        #     is_terminal = True
        # else:
        #     is_terminal = False

        if player == g.tree.players[0]:
            player_id = g.ids.PLAYER1
        elif player == g.tree.players[1]:
            player_id = g.ids.PLAYER2
        elif player == g.tree.players.chance:
            player_id = g.ids.CHANCE
        elif is_terminal:
            player_id = g.ids.TERMINAL

           
            # we also have to set the node outcome
            # first, check if the potential showdown winner had folded 
            folder = get_folder(g, action, bets)

            # if we're here on the first round of betting, someone must've folded...
            if winner is None and bet_round == 1:

                # set winner to be the non-folder
                winner = get_other_player(g, folder)

            # if the winner folded
            if winner is not None and winner == folder:

                # swap winner with other player
                winner = get_other_player(g, winner)

            # second, need to see how much they win
            amount = get_amount(g, winner, bets)

            # third, we get the outcome
            outcome = g.get_outcome(winner, amount)

            # finally, we set the outcome
            node.outcome = outcome

        else:
            raise Exception("I have no idea what player this is: {}".format(player))
        
        # given C0-A0-B, we might want to create the new id C0-A0-B0-T = UNIQUE_ID_PARENT + 0-T
        UNIQUE_ID = "{}{}{}-{}".format(UNIQUE_ID_PARENT, action, child_index, player_id)

    # this is the label we'd like to return
    # label = "{} - {}".format(UNIQUE_ID, NODE_DESCRIPTION)
    label = "{}".format(UNIQUE_ID)

    return label


def get_other_player(g, player):
    '''
    Get the other player in the game.
    '''
    
    other_player = None

    if player == g.tree.players[0]:
        other_player = g.tree.players[1]
    else:
        other_player = g.tree.players[0]

    return other_player


def get_winner(g, bet_round):
    '''
    Returns the winner of the current scenario.
    '''

    # ... we need to see who wins the showdown
    winner = dw.get_showdown_winner(g, bet_round)

    return winner


def get_folder(g, action, bets):
    '''
    Returns the winner of the current scenario.
    '''

    # the winner we'd like to return
    folder = None
    
    # if someone folded... 
    if action == g.ids.FOLD:

        # we need to see who folded
        # if player 1 folded...
        if bets[0] < bets[1]:

            # return player 2
            folder = g.tree.players[0]

        # if player 2 folded...
        elif bets[0] > bets[1]:

            # return player 1
            folder = g.tree.players[1]

        else:
            error_msg  = "We are told that someone folded, but both players have the same bet. bets: {}"
            raise Exception(error_msg.format(bets))

    return folder
        

def get_amount(g, winner, bets):
    '''
    Get amount won.
    '''

    # if we have a tie
    if winner == None:
        amount = 0

    # it's just the minimum payoff
    else:
        amount = min(bets[0], bets[1])

    return amount


def get_deal_string(g, bet_round, child_index):

    # we need the chance round for which the cards are being dealt, 
    # and which cards were dealt
    current_round = get_round(g, bet_round)
    template = current_round.deal_string_template
    if bet_round == 1:
        hole_cards = g.get_hole_cards()
        return_str = template.format(g.tree.players[0].label, 
                                     hole_cards[0],
                                     hole_cards[1],
                                     g.tree.players[1].label, 
                                     hole_cards[2],
                                     hole_cards[3])
    elif bet_round == 2:
        flop_cards = g.get_flop_cards()
        return_str = template.format(flop_cards[0],
                                     flop_cards[1],
                                     flop_cards[2])
    elif bet_round == 3:
        turn_card = g.get_hole_cards()
        return_str = template.format(turn_card)
    elif bet_round == 4:
        river_card = g.get_hole_cards()
        return_str = template.format(river_card)
    else:
        raise Exception("Bad bet_round was given: {}".format(bet_round))

    # we also want to prepend the child number to the string
    return_str = "{}. {}".format(child_index, return_str)

    return return_str


def get_minimum_deck_size(n):
    '''
    Returns the minimum deck size, given the number of rounds.
    n: the number of rounds
    '''

    # need 4 cards for the hole cards
    if n == 1:
        return 4

    # need 3 cards for the flop
    elif n == 2:
        return 7
    
    # need 1 card for the turn
    elif n == 3:
        return 8

    # need 1 card for the river
    elif n == 4:
        return 9
    
    # n should only be in {1,2,3,4}
    else:
        raise Exception("Bad value for NUMBER_OF_ROUNDS. Should be from 1 to 4. Given ({})".format(n))


def is_round(g, n, bet_round):
    number_of_rounds = g.get_number_of_rounds()
    last_round = False
    if type(bet_round) is not int:
        raise Exception("bet_round is type ({}) but should be type int".format(type(bet_round)))
    elif bet_round == n:
        last_round = True
    elif bet_round != 1 and bet_round != 2 and bet_round != 3 and bet_round != 4:
        raise Exception("bad bet_round value ({}) given".format(bet_round))
    return last_round


def is_last_round(g, bet_round):
    '''
    Returns True if this is the last round.
    '''

    return is_round(g, g.get_number_of_rounds(), bet_round)


def is_turn_round(g, bet_round):
    '''
    Returns True if this is the flop round.
    '''

    return is_round(g, 3, bet_round)


def is_river_round(g, bet_round):
    '''
    Returns True if this is the flop round.
    '''

    return is_round(g, 4, bet_round)


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
    for i in range(g.get_number_of_rounds()):
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


def min_val_rec(x, MAX, length):
    
    # error handler
    if x < 0 or type(x) is not int:
        error_msg = "Can't calculate a recursion for x={}"
        raise Exception(error_msg.format(x))

    min_value = 0
    if length == 3:
        for i in range((MAX-1)-x, MAX-1): # we don't include MAX-1
            min_value += math.sum_first_n_values(i)

    elif length == 2:
        for i in range((MAX)-x, MAX): # we don't include MAX
            min_value += i

    return min_value


def checks(cards, MAX, expected_deck_sizes):
    
    # if we're looking at an int, change to a list
    if type(expected_deck_sizes) is int:
        expected_deck_sizes = [expected_deck_sizes]

    # if we don't pass in a list
    if type(cards) is not list:
        error_msg = "cards must be an int or a list. cards currently is of type {}"
        raise Exception(error_msg.format(type(cards)))

    # we don't handle lists greater than length 7
    if len(cards) not in expected_deck_sizes:
        error_msg = "The length of cards is {} and should be {}."
        raise Exception(error_msg.format(len(cards), expected_deck_sizes))

    # values in the list should be ints
    for card in cards:
        if type(card) is not int:
            error_msg = "each card should have ints as values; not {}"
            raise Exception(error_msg.format(type(card)))
        
        # if cards[0] is greater than MAX, that's a problem
        if card >= MAX:
            error_msg = "card={} which is greater than MAX=({})"
            raise Exception(error_msg.format(card, MAX))


def get_order(cards, MAX):
    '''
    Return the index of the the cst that handles creating the subtree for these cards
    '''

    # if we just passed in an int, then return the int -- it's its own index
    if type(cards) is int:
        cards = [cards] 
    
    # checks to see if cards is a good list of cards
    checks(cards, MAX, [1,2,3])

    # if we just passed in an int, then return the int -- it's its own index
    if len(cards) == 1:
        return cards[0]

    # save the value of the first card
    x = cards[0]
    min_index = 0

    # then we have to find the minimum index, given the first card:
    min_index = min_val_rec(x, MAX, len(cards))

    modifier = x + 1
    for i in range(1, len(cards)):
        cards[i] -= modifier
    MAX -= modifier

    order = min_index + get_order(cards[1:], MAX)

    return order


def get_order_helper(cards, MAX, expected_deck_size, pf_n):
    
    # checks to see if cards is a good list of cards
    checks(cards, MAX, expected_deck_size)
    
    # we want to get the order given that any previous values in the list 
    # won't be there in the new list, altering the indices...
    modified_cards = []
    reverse_cards = cards[:pf_n]
    reverse_cards.sort()
    reverse_cards.reverse()

    for modified_card in cards[pf_n:]:
        for compare_card in reverse_cards:
            if modified_card > compare_card:
                modified_card -= 1
        modified_cards.append(modified_card)

    # relative order
    return_order = get_order(modified_cards, MAX-pf_n)

    return return_order


def get_order_chooser(card_ints, MAX):
    orders = None
    sorted_card_ints = []
    error_msg = '''Valid size for the list of cards are: 4, 7, 8, 9. 
                        Current size is {}.'''

    if len(card_ints) >= 4:
        player1_card_ints = card_ints[:2]
        player2_card_ints = card_ints[2:4]
        player1_card_ints.sort()
        player2_card_ints.sort()
        sorted_card_ints += player1_card_ints
        sorted_card_ints += player2_card_ints
        if len(card_ints) >= 7:
            flop_card_ints    = card_ints[4:7]
            flop_card_ints.sort()
            sorted_card_ints += flop_card_ints
            if len(card_ints) >= 8:
                turn_card_ints    = card_ints[7:8]
                turn_card_ints.sort()
                sorted_card_ints += turn_card_ints
                if len(card_ints) >= 9:
                    river_card_ints   = card_ints[8:9]
                    river_card_ints.sort()
                    sorted_card_ints += river_card_ints
                    if len(card_ints) == 9:
                        orders = get_order_hole_flop_turn_river(sorted_card_ints, MAX)
                    else:
                        raise Exception(error_msg.format(card_ints))
                else:
                    orders = get_order_hole_flop_turn(sorted_card_ints, MAX)
            else:
                orders = get_order_hole_flop(sorted_card_ints, MAX)
        else:
            orders = get_order_hole(sorted_card_ints, MAX)
    else:
        raise Exception(error_msg.format(card_ints))

    return orders


def get_order_hole(cards, MAX):
    
    # checks to see if cards is a good list of cards
    order2 = get_order_helper(cards, MAX, 4, 2)
    
    # number of combinations given a fixed first pair
    combos_given_pair1 = math.combinations(MAX-2, 2)

    # order of the first pair
    order1 = get_order(cards[0:2], MAX)

    # the actual order, given both pairs
    order = (order1 * combos_given_pair1) + order2

    return [order]
    

def get_order_hole_flop(cards, MAX):

    order_flop = get_order_helper(cards, MAX, 7, 4)

    remaining_orders = get_order_hole(cards[:4], MAX)

    remaining_orders.append(order_flop)

    return remaining_orders


def get_order_hole_flop_turn(cards, MAX):

    # checks to see if cards is a good list of cards
    order_turn = get_order_helper(cards, MAX, 8, 7)

    remaining_orders = get_order_hole_flop(cards[:7], MAX)

    remaining_orders.append(order_turn)

    return remaining_orders


def get_order_hole_flop_turn_river(cards, MAX):

    # checks to see if cards is a good list of cards
    order_river = get_order_helper(cards, MAX, 9, 8)

    remaining_orders = get_order_hole_flop_turn(cards[:8], MAX)

    remaining_orders.append(order_river)

    return remaining_orders


if __name__ == '__main__':

    # create the game tree and saver objects, solve the game, print the solutions to a file, print the game
    s = compute_time_of(0, "Creating Saver", common.create_saver, ())
    g = compute_time_of(1, "Creating Game", create_game, (sys.argv,))
    try:
        compute_time_of(2, "Creating Tree", create_tree, (g,))
        # solutions = compute_time_of(3, "Solving Game", common.solve_game, (g,))
        # compute_time_of(4, "Printing Solutions", common.print_solutions, (solutions,s)) 
    except (KeyboardInterrupt):
        pass
    compute_time_of(5, "Printing Game", common.print_game, (g,s))
