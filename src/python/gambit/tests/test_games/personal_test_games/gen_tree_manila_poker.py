# libraries that are built-in to python
import os, sys, distutils
from time import time, strftime
from distutils    import util
from fractions    import Fraction
from numbers      import Rational
from ConfigParser import ConfigParser
from ast          import literal_eval
from copy         import deepcopy
import itertools

# libraries from GitHub
import gambit, deuces

# custom libraries
import math_extended as math
from utils import compute_time_of
import common
import deuces_wrapper as dw


class Action(object):
    '''
    These are strings that will identify which characters performed which 
    actions at a specific moments. This is primarily seen in the output file.
    '''

    def __init__(self, g, identifier):

        # actions and characters
        self.identifier = identifier
        if identifier == g.ids.BET:
            full_name = "bets"
        elif identifier == g.ids.CHECK:
            full_name = "checks"
        elif identifier == g.ids.CALL:
            full_name = "calls"
        elif identifier == g.ids.FOLD:
            full_name = "folds"
        elif identifier == g.ids.RAISE:
            full_name = "raise"
        else:
            error_msg = "This is not a valid identifier: {}"
            raise Exception(error_msg.format(identifier))
        self.template = "{}. {} " + full_name

    # def __str__(self):
    #     '''
    #     We want a string method 
    #     '''

    #     # the string to return
    #     string = None

    #     return string

    def get_identifier(self):
        return self.identifier

    def get_full_name(self):
        return self.full_name

    def get_template(self, n, player):
        formatted_string = self.template.format(n, player.label)
        return formatted_string


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
                 SHORT_LABELS,
                 PLAYER,
                 SPECIFIC_HOLE=[],
                 SPECIFIC_ACTIONS1=[],
                 SPECIFIC_FLOP=[],
                 SPECIFIC_ACTIONS2=[],
                 SPECIFIC_TURN=[],
                 SPECIFIC_ACTIONS3=[],
                 SPECIFIC_RIVER=[],
                 SPECIFIC_ACTIONS4=[]):

        def check_specific_cards_and_actions(self, SPECIFIC_HOLE, 
            SPECIFIC_ACTIONS1, SPECIFIC_FLOP,  SPECIFIC_ACTIONS2,
            SPECIFIC_TURN, SPECIFIC_ACTIONS3, SPECIFIC_RIVER, 
            SPECIFIC_ACTIONS4):

            # we should check whether there is anything wrong with our given cards
            # and actions, and caao is short for "cards and actions ordered"
            acaao = [ (SPECIFIC_HOLE,     "SPECIFIC_HOLE",     "cards",   2, 2),
                      (SPECIFIC_ACTIONS1, "SPECIFIC_ACTIONS1", "actions", 0, 3),
                      (SPECIFIC_FLOP,     "SPECIFIC_FLOP",     "cards",   0, 3),
                      (SPECIFIC_ACTIONS2, "SPECIFIC_ACTIONS2", "actions", 0, 3),
                      (SPECIFIC_TURN,     "SPECIFIC_TURN",     "cards",   0, 1),
                      (SPECIFIC_ACTIONS3, "SPECIFIC_ACTIONS3", "actions", 0, 3),
                      (SPECIFIC_RIVER,    "SPECIFIC_RIVER",    "cards",   0, 1),
                      (SPECIFIC_ACTIONS4, "SPECIFIC_ACTIONS4", "actions", 0, 3) ]
            
            # this keys track of our first incomplete list of cards or actions
            first_incomplete_coa = None

            # list of all possible sequences of complete actions
            valid_complete_actions = [
                ["B", "R", "K"],
                ["B", "R", "F"],
                ["B", "K"],
                ["B", "F"],
                ["C", "B", "K"],
                ["C", "B", "F"],
                ["C", "C"]
            ]

            # list of all possible sequences of incomplete actions
            valid_incomplete_actions = [
                ["B", "R"],
                ["B"],
                ["C", "B"],
                ["C"],
                []
            ]
            
            # cards that have been seen so far
            seen_cards = []

            # for every card or action, or cao...
            for index_coa in range(len(acaao)):
                coa_tuple = acaao[index_coa]

                # get the values in which we're interested
                coa           = coa_tuple[0]
                len_coa       = len(coa)
                name          = coa_tuple[1]
                object_types  = coa_tuple[2]
                min_len       = coa_tuple[3]
                max_len       = coa_tuple[4]

                # check the lengths
                if len_coa < min_len:
                    error_msg = '''List for {} too short. 
                    Number of {} provided must be at least {}.'''
                    raise Exception(error_msg.format(name, object_types, min_len))
                if len_coa > max_len:
                    error_msg = '''List for {} too long. 
                    Number of {} provided must be at most {}.'''
                    raise Exception(error_msg.format(name, object_types, max_len))

                if object_types == "cards" and (min_len < len_coa < max_len):
                    error_msg = '''List of cards for {} has bad length. 
                    Must be of length {} or {}.'''
                    raise Exception(error_msg.format(name, min_len, max_len))

                # check if we're looking at an invalid list of actions
                if object_types == "actions":
                    if coa not in valid_incomplete_actions and \
                       coa not in valid_complete_actions:
                        error_msg = "{} is an impossible list of actions."
                        raise Exception(error_msg.format(name))

                # check for complete cards or actions
                if not first_incomplete_coa:
                    if object_types == "actions": 
                        if coa in valid_incomplete_actions:
                            first_incomplete_coa = name
                    elif object_types == "cards":
                        if len_coa == 0:
                            first_incomplete_coa = name

                # if we have an incomplete list of actions or cards...
                # we need to ensure we have aren't specifying any more cards or 
                # actions
                elif first_incomplete_coa:
                    if object_types == "actions": 
                        if coa:
                            error_msg = '''List for {} should be empty since the 
                            list for {} was incomplete.'''
                            raise Exception(
                                error_msg.format(name, acaao[index_coa-1][1]))
                    elif object_types == "cards":
                        if coa:
                            error_msg = '''List for {} should be empty since the 
                            list for {} was incomplete.'''
                            raise Exception(
                                error_msg.format(name, acaao[index_coa-1][1]))

                # check cards to ensure valid and not including duplicates
                if object_types == "cards": 
                    for card in coa:
                        
                        # if the card isn't in our deck of allowed cards
                        if card not in self.initial_deck:
                            error_msg = '''{} is not a valid card in {}.'''
                            raise Exception(error_msg.format(card, name))
                        
                        # if the card is a duplicate
                        if card in seen_cards:
                            error_msg = '''Duplicates of {} were given.'''
                            raise Exception(error_msg.format(card))

                        seen_cards.append(card)


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
        self.initial_deck      = self.create_card_labels()
        self.cards_to_ints_map = self.create_card_to_ints_map()

        # we need to globally keep track of the betting round we're on
        self.deal_sizes    = [self.HAND_SIZE,
                              self.FLOP_SIZE,
                              self.TURN_SIZE,
                              self.RIVER_SIZE]

        # we should check whether there is anything wrong with our given cards
        # and actions
        check_specific_cards_and_actions(self, SPECIFIC_HOLE, 
            SPECIFIC_ACTIONS1, SPECIFIC_FLOP,  SPECIFIC_ACTIONS2,
            SPECIFIC_TURN, SPECIFIC_ACTIONS3, SPECIFIC_RIVER, 
            SPECIFIC_ACTIONS4)

        # we need to globally keep track of the names, amounts to deal, any 
        # repititions in dealing, and the indexof the branch we're currently
        # looking at
        self.rounds = [Round(name                 = "Hole",  
                             deal_size            = self.HAND_SIZE,  
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "{} received ({},{}) and {} received ({},{}).",
                             deck                 = [],
                             debug_cards          = SPECIFIC_HOLE[:],
                             current_cards        = SPECIFIC_HOLE[:],
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS1), 
                       Round(name                 = "Flop",  
                             deal_size            = self.FLOP_SIZE, 
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "Flop cards were ({},{},{}).",
                             deck                 = [],
                             debug_cards          = SPECIFIC_FLOP[:],
                             current_cards        = SPECIFIC_FLOP[:],
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS2), 
                       Round(name                 = "Turn",  
                             deal_size            = self.TURN_SIZE,  
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "Turn card was {}.",
                             deck                 = [],
                             debug_cards          = SPECIFIC_TURN[:],
                             current_cards        = SPECIFIC_TURN[:],
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS3), 
                       Round(name                 = "River", 
                             deal_size            = self.RIVER_SIZE, 
                             repeat               = 1, 
                             child_index          = 0, 
                             deal_string_template = "River card was {}.",
                             deck                 = [],
                             debug_cards          = SPECIFIC_RIVER[:],
                             current_cards        = SPECIFIC_RIVER[:],
                             debug_child_index    = None,
                             debug_actions        = SPECIFIC_ACTIONS4)]

        # testing purposes
        self.DEBUG        = DEBUG
        self.SHORT_LABELS = SHORT_LABELS

        # we also want to set the cards and actions that were specified
        self.PLAYER = PLAYER

        # mappings for Manila Poker
        self.mpm = dw.Manila_Poker_Mapping()

        # variable to keep track of the tree
        self.tree = None

        # actions and players identifiers
        self.ids = Identifiers()

        # get a list of all possible paths
        # self.action_round_paths = [
        #     (),
        #     (self.ids.BET,),
        #     (self.ids.CHECK,),
        #     (self.ids.BET,   self.ids.RAISE),
        #     (self.ids.BET,   self.ids.CALL),
        #     (self.ids.BET,   self.ids.FOLD),
        #     (self.ids.CHECK, self.ids.BET),
        #     (self.ids.CHECK, self.ids.CHECK),
        #     (self.ids.BET,   self.ids.RAISE, self.ids.CALL),
        #     (self.ids.BET,   self.ids.RAISE, self.ids.FOLD),
        #     (self.ids.CHECK, self.ids.BET,   self.ids.CALL),
        #     (self.ids.CHECK, self.ids.BET,   self.ids.FOLD)
        # ]

        self.action_round_paths = [
            ''.join((self.ids.NO_ACTION,)),                           # 0  : ""
            ''.join((self.ids.BET,)),                                 # 1  : "B"
            ''.join((self.ids.CHECK,)),                               # 2  : "C"
            ''.join((self.ids.BET,   self.ids.RAISE)),                # 3  : "BR"
            ''.join((self.ids.BET,   self.ids.CALL)),                 # 4  : "BK"
            ''.join((self.ids.BET,   self.ids.FOLD)),                 # 5  : "BF"
            ''.join((self.ids.CHECK, self.ids.BET)),                  # 6  : "CB"
            ''.join((self.ids.CHECK, self.ids.CHECK)),                # 7  : "CC"
            ''.join((self.ids.BET,   self.ids.RAISE, self.ids.CALL)), # 8  : "BRK"
            ''.join((self.ids.BET,   self.ids.RAISE, self.ids.FOLD)), # 9  : "BRF"
            ''.join((self.ids.CHECK, self.ids.BET,   self.ids.CALL)), # 10 : "CBK"
            ''.join((self.ids.CHECK, self.ids.BET,   self.ids.FOLD))  # 11 : "CBF"
        ]

        # we need a mapping of infoset labels to infosets
        self.infoset_mapping = {}

        # the mapping from actions to their respective indices in the tree
        # self.atim = {
        #     self.action_round_paths[0]  : [],
        #     self.action_round_paths[1]  : [0],
        #     self.action_round_paths[2]  : [1],
        #     self.action_round_paths[3]  : [0, 0],
        #     self.action_round_paths[4]  : [0, 1],
        #     self.action_round_paths[5]  : [0, 2],
        #     self.action_round_paths[6]  : [1, 0],
        #     self.action_round_paths[7]  : [1, 1],
        #     self.action_round_paths[8]  : [0, 0, 0],
        #     self.action_round_paths[9]  : [0, 0, 1],
        #     self.action_round_paths[10] : [1, 0, 0],
        #     self.action_round_paths[11] : [1, 0, 1]
        # }

        self.winner        = None
        self.player1_class = None
        self.player2_class = None


    def set_debug_child_index(self, HOLE, FLOP, TURN, RIVER):
        '''
        We'd like to represent the node as [int, int, int, int] where 
        each int is supposed to represent the child index. 
        '''

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


        def get_order_chooser(card_ints, MAX):
            orders = None
            sorted_card_ints = []
            error_msg = '''Valid size for the list of cards are: 4, 7, 8, 9. 
                                Current size is {}.'''

            if len(card_ints) >= 2:
                player1_card_ints = card_ints[:2]
                player1_card_ints.sort()
                sorted_card_ints += player1_card_ints
                if len(card_ints) >= 7:
                    flop_card_ints = card_ints[4:7]
                    flop_card_ints.sort()
                    sorted_card_ints += flop_card_ints
                    if len(card_ints) >= 8:
                        turn_card_ints = card_ints[7:8]
                        turn_card_ints.sort()
                        sorted_card_ints += turn_card_ints
                        if len(card_ints) >= 9:
                            river_card_ints = card_ints[8:9]
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
        deck = self.get_initial_deck()
        
        # create the mapping
        mapping = {}

        # for every card...
        for card in range(len(deck)):
            
            # add it to the mapping
            mapping[deck[card]] = card

        return mapping


    def get_hole_cards(self):
        
        # if the game is focused on player 1...
        if self.PLAYER == self.tree.players[0]:
            player_1_cards = self.rounds[0].current_cards[:2]
            player_2_cards = self.rounds[0].current_cards[2:]
        
        # if the game is focused on player 2...
        else:
            player_1_cards = self.rounds[0].current_cards[2:]
            player_2_cards = self.rounds[0].current_cards[:2]

        hole_cards = player_1_cards + player_2_cards

        return hole_cards


    def get_flop_cards(self):
        flop_cards = self.rounds[1].current_cards[:]
        return flop_cards


    def get_turn_card(self):
        turn_card = self.rounds[2].current_cards[:]
        return turn_card


    def get_river_card(self):
        river_card = self.rounds[3].current_cards[:]
        return river_card


    def get_cards_in_play(self, bet_round):
        
        cards_in_play  = []
        
        if bet_round >= 1:
            cards_in_play += self.get_hole_cards()
            if bet_round >= 2:
                cards_in_play += self.get_flop_cards()
                if bet_round >= 3:
                    cards_in_play += self.get_turn_card()
                    if bet_round >= 4:
                        cards_in_play += self.get_river_card()
        
        return cards_in_play


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


    def get_initial_deck(self):
        return self.initial_deck


    # def set_infosets(self):

    #     # if we're making the tree for player 1... 
    #     if self.PLAYER == self.g.players[0]:

    #         # we want to get all possible, relevant, action paths for the labels

    #         # Terminating: ["", "BR", "CB"]
    #         terminating = []
    #         terminating.append(action_round_paths[0])  # 0  : ""
    #         terminating.append(action_round_paths[3])  # 3  : "BR"
    #         terminating.append(action_round_paths[6])  # 6  : "CB"

    #         # Recursive: ["BK", "CC", "BRK", "CBK"]
    #         recursive = []
    #         terminating.append(action_round_paths[4])  # 4  : "BK"
    #         terminating.append(action_round_paths[7])  # 7  : "CC"
    #         terminating.append(action_round_paths[8])  # 8  : "BRK"
    #         terminating.append(action_round_paths[10]) # 10 : "CBK"

    #         # add all possible combinations
    #         # get all products of recursives from 0 to 3
    #         combinations = []
    #         for i in range(4):
    #             combinations += list(itertools.product(recursive, repeat=i))

    #         # and get the product of all possible combinations with everything
    #         # this should give us all possible paths of length 1-4
    #         combinations += list(itertools.product(combinations, terminating+recursive))

    #         # now we need to add an infoset to self.g.infosets for every label 
    #         # (about 595 labels altogether at this point)
    #         for combination_index in range(len(combinations)):
    #             combination = combinations[combination_index]
    #             self.g.infosets.append(combination)


    #     # otherwise we're making the tree for player 2...
    #     elif self.PLAYER == self.g.players[1]:
    #         pass

    #     # we shouldn't get here...    
    #     else:
    #         raise Exception("Bad player specified to make tree: {}".format(self.PLAYER))


class Round(object):

    def __init__(
        self, 
        name, 
        deal_size, 
        repeat, 
        child_index, 
        deal_string_template, 
        deck,
        debug_cards,
        current_cards,
        debug_child_index, 
        debug_actions):
        
        self.name                 = name
        self.deal_size            = deal_size
        self.repeat               = repeat
        self.child_index          = child_index
        self.deal_string_template = deal_string_template
        self.deck                 = deck
        self.debug_cards          = debug_cards
        self.current_cards        = current_cards
        self.debug_child_index    = debug_child_index
        self.debug_actions        = debug_actions


    def set_deck(self, deck):
        self.deck = deck


def create_game():

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
                                   SAVED_GAMES_DIRECTORY (str)
                                   OUTPUTS_DIRECTORY (str)
                                   OUTPUT_DIRECTORY (str with '{}')
                                   GAME_TREE_FILE (str)
                                   EXPECTED_VALUES_FILE (str)
                                   SOLUTIONS_FILE (str)
                                   DEBUG (bool)
                                   SHORT_LABELS (bool)
                                   PLAYER (PLAYER_1 or PLAYER_2)
                                   SPECIFIC_HOLE (list or None)
                                   SPECIFIC_ACTIONS1 (list or None)
                                   SPECIFIC_FLOP (list or None)
                                   SPECIFIC_ACTIONS2 (list or None)
                                   SPECIFIC_TURN (list or None)
                                   SPECIFIC_ACTIONS3 (list or None)
                                   SPECIFIC_RIVER (list or None)
                                   SPECIFIC_ACTIONS4 (list or None)]"""

    try:

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
        SHORT_LABELS      = distutils.util.strtobool(cfg.get(TESTING_SECTION,"SHORT_LABELS"))
        PLAYER            = cfg.get(TESTING_SECTION,"PLAYER")
        SPECIFIC_HOLE     = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_HOLE"))
        SPECIFIC_ACTIONS1 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS1"))
        SPECIFIC_FLOP     = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_FLOP"))
        SPECIFIC_ACTIONS2 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS2"))
        SPECIFIC_TURN     = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_TURN"))
        SPECIFIC_ACTIONS3 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS3"))
        SPECIFIC_RIVER    = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_RIVER"))
        SPECIFIC_ACTIONS4 = literal_eval(cfg.get(TESTING_SECTION,"SPECIFIC_ACTIONS4"))
        
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
        if PLAYER != "PLAYER_1" and PLAYER != "PLAYER_2":
            message += "PLAYER must be either PLAYER_1 or PLAYER_2. ({}) was provided.".format(PLAYER)
        if message != "":
           raise Exception(message)
    
    # stop the script if anything went wrong
    except ValueError():
        print(USAGE_OUTPUT)
        sys.exit(2)

    # if Nones were specified for debug cards, transform them to empty lists
    if not SPECIFIC_HOLE:
        error_msg = "SPECIFIC_HOLE cannot be empty. Given SPECIFIC_HOLE ({})"
        raise Exception(error_msg.format(SPECIFIC_HOLE))   
    if SPECIFIC_FLOP  is None:
        SPECIFIC_FLOP  = []
    if SPECIFIC_TURN  is None:
        SPECIFIC_TURN  = []
    if SPECIFIC_RIVER is None:
        SPECIFIC_RIVER = []

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
              SHORT_LABELS=SHORT_LABELS,
              PLAYER=PLAYER,
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

    # set the focus player
    if PLAYER == "PLAYER_1":
        g.PLAYER = g.tree.players[0]

    elif PLAYER == "PLAYER_2":
        g.PLAYER = g.tree.players[1]

    else:
        error_msg = '''({}) is an unrecognized option for PLAYER.
        Valid options are PLAYER_1 or PLAYER_2.'''
        raise Exception(error_msg.format(PLAYER))

    # set the title
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


def create_tree(g):


    def prune_tree():
        '''
        We want to replace the children of the root node with the focus node.
        '''

        # we must have the first chance node 
        # opdi = other player deal index
        for opdi in range(len(g.tree.root.children)):
            
            # the node we'll replace
            node_to_replace = g.tree.root.children[opdi]

            # the node we'd like to focus on... we have to find it first
            focus_node = node_to_replace

            # at this point, we'll keep on seeing nodes with one branch until
            # our branch of node
            while len(focus_node.children) == 1:

                # look at the next node in the height of the tree
                focus_node = focus_node.children[0]

            # move the subtree
            # focus_node.move_tree(node_to_replace)
            while focus_node.parent != g.tree.root: 
                focus_node.delete_parent()


        # we should update our g.infoset_mapping dictionary
        actions = g.rounds[0].debug_actions + g.rounds[1].debug_actions + g.rounds[2].debug_actions + g.rounds[3].debug_actions
        actions = "".join(actions)

        # get the keys
        keys = g.infoset_mapping.keys()
        for key in keys:
            if len(key) < len(actions):
                del g.infoset_mapping[key]


    print("Beginning to compute payoff tree".format(g.tree.title))

    # we want to start this tree by creating a chance node
    create_cst(g=g, 
               root=g.tree.root,
               # we're setting this to zero when there are 2 players
               repeat=len(g.tree.players)-2, 
               bet_round=1,
               pot=0)

    # prune the tree
    prune_tree()


def create_cst(g, root, repeat, bet_round, pot, action=""):
    """
    g: the game itself
    root: the node for which we'd like to create the cst   
    repeat: the number of times we'll deal the cards
    combinations: the number combinations we have so far
    """

    def set_deck(g, bet_round):
        '''
        We need to return the number of branches we should be creating. 
        '''

        # get the number of cards we need to deal out
        deal_size = get_deal_size(g, bet_round)

        # get the decks we'll be modifying
        default_deck = g.get_initial_deck()
        cards_to_remove = []

        # if it's the first chance round... 
        if bet_round == 1:

            # we need to add: 
            #    2 hole cards
            #    3 flop cards (if specified)
            #    1 turn card  (if specified)
            #    1 river card (if specified)
            cards_to_remove += g.rounds[0].current_cards
            if g.rounds[1].debug_cards:
                cards_to_remove += g.rounds[1].debug_cards
                if g.rounds[2].debug_cards:
                    cards_to_remove += g.rounds[2].debug_cards
                    if g.rounds[3].debug_cards:
                        cards_to_remove += g.rounds[3].debug_cards

            # remove the cards                        
            get_round(g, bet_round).set_deck([x for x in default_deck if x not in cards_to_remove])
            
        # if it's the second chance round...
        elif bet_round == 2:

            # if we've specified the flop cards, then we only need one branch...
            if g.rounds[1].debug_cards:
                get_round(g, bet_round).set_deck(g.rounds[1].debug_cards[:])

            else:
                # we need to add: 
                #    2+2 hole cards
                #    1 turn card  (if specified)
                #    1 river card (if specified)
                cards_to_remove += g.rounds[0].current_cards
                if g.rounds[2].debug_cards:
                    cards_to_remove += g.rounds[2].debug_cards
                    if g.rounds[3].debug_cards:
                        cards_to_remove += g.rounds[3].debug_cards

                # remove the cards
                get_round(g, bet_round).set_deck([x for x in default_deck if x not in cards_to_remove])

        # if it's the third chance round...
        elif bet_round == 3:
            
            # if we've specified the flop cards, then we only need one branch...
            if g.rounds[2].debug_cards:
                get_round(g, bet_round).set_deck(g.rounds[2].debug_cards[:])

            else:
                # we need to add: 
                #    2+2 hole cards
                #    3 flop cards
                #    1 river card (if specified)
                cards_to_remove += g.rounds[0].current_cards
                cards_to_remove += g.rounds[1].current_cards
                if g.rounds[3].debug_cards:
                    cards_to_remove += g.rounds[3].debug_cards
                
                # remove the cards
                get_round(g, bet_round).set_deck([x for x in default_deck if x not in cards_to_remove])

        # if it's the fourth chance round...
        elif bet_round == 4:
            
            # if we've specified the flop cards, then we only need one branch...
            if g.rounds[3].debug_cards:
                get_round(g, bet_round).set_deck(g.rounds[3].debug_cards[:])

            else:
                # we need to add: 
                #    2+2 hole cards
                #    3 flop cards
                #    1 turn card
                cards_to_remove += g.rounds[0].current_cards
                cards_to_remove += g.rounds[1].current_cards
                cards_to_remove += g.rounds[2].current_cards

                # remove the cards
                get_round(g, bet_round).set_deck([x for x in default_deck if x not in cards_to_remove])


    # we want to hole on to the number of combinations we can deal out
    number_of_deal_combinations = 1
    
    # get the number of cards we need to deal out
    deal_size = get_deal_size(g, bet_round)

    # compute the amount
    number_of_dealings_iterable = range(repeat+1)

    # set this round's deck
    set_deck(g, bet_round)
    deck_size = len(get_deck(g, bet_round))

    for number in number_of_dealings_iterable:
      
        # Calculate the number of card combinations for this round
        number_of_deal_combinations *= math.combinations(deck_size, deal_size)

        # adjust the deal_size in case we need have one more dealing
        # deck_size -= deal_size

    # create the branches
    iset_chance = root.append_move(g.tree.players.chance, number_of_deal_combinations)

    # label the chance node
    round_name        = get_round(g, bet_round).name
    node_label_suffix = "Chance node for {} Round".format(round_name)
    bets              = (pot/2, pot/2)
    root.label        = set_node_label(g, root, bet_round, node_label_suffix, False, action, bets)
    
    # set the members index to zero
    set_child_index(g, bet_round, 0)

    # populated the branches that were just created
    populate_cst(g, iset_chance, repeat, bet_round, pot, [])


def populate_cst(g, iset_chance, repeat, bet_round, pot, all_cards):

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
            turn_card = g.get_turn_card()[0]
            return_str = template.format(turn_card)
        elif bet_round == 4:
            river_card = g.get_river_card()[0]
            return_str = template.format(river_card)
        else:
            raise Exception("Bad bet_round was given: {}".format(bet_round))

        # we also want to prepend the child number to the string
        return_str = "{}. {}".format(child_index, return_str)

        return return_str

    # get the number of cards we need to deal out
    deal_size = get_deal_size(g, bet_round)

    # get the decks we'll be modifying
    current_deck_index = bet_round
    current_deck = get_deck(g, bet_round)

    # get all possible combinations we want to iterate over
    all_combinations = list(itertools.combinations(current_deck, deal_size))
    
    # for every combination...
    for deal_index in range(len(all_combinations)):

        deal = all_combinations[deal_index]
        current_cards_in_play = g.get_cards_in_play(bet_round)
        
        # get the current round
        current_round = get_round(g, bet_round)

        # if it's the first bet round
        # or if it's not the first bet round adn the debug cards are empty
        if bet_round == 1 or (bet_round != 1 and not get_round(g, bet_round).debug_cards):
            current_round.current_cards += list(deal)

        # we need to label the branch
        deal_string = get_deal_string(g, bet_round, deal_index)
        iset_chance.actions[deal_index].label = deal_string

        # get the current child itself...
        child = iset_chance.members[0].children[deal_index]

        # create the bst for the child node
        create_bst(g, child, iset_chance, deal_size, bet_round, pot)

        # reset the current_round cards
        current_round.current_cards = current_round.debug_cards[:]


def create_bst(g, root, iset_bet, deal_size, bet_round, pot):
    
    def get_child(root, specific_index):
        '''
        We want to return the appropriate child.
        '''

        num_children = len(root.children)

        # if we only have one child, return the first child
        if num_children == 1:
            child = root.children[0]
        
        # otherwise, return the specific child we should be requesting...
        elif num_children == 2 or num_children == 3:
            child = root.children[specific_index]

        else:
            error_msg = "node {} has {} children, but should have 1, 2, or 3 children."
            raise Exception(error_msg.format(root.label, num_children))

        return child

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
    # we only calculate the winner if it's the last round
    if bet_round != g.get_number_of_rounds():
        (g.winner, g.player1_class, g.player2_class) = (None, None, None)
    else:
        (g.winner, g.player1_class, g.player2_class) = dw.get_showdown_winner(g, bet_round)

    ###############################################
    ########## CREATE ROW 1 AND BRANCHES ##########
    ###############################################

    # we are interested in just the first action, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:0]:
        specific_actions_so_far += specific_action

    # we need to create player 1's betting and checking branches
    actions_so_far = g.action_round_paths[0]
    if actions_so_far.startswith(specific_actions_so_far):
        action = g.ids.NO_ACTION
        node = root
        player = p1
        # action_labels = ["{}. {} bets", "{}. {} checks"]
        action_labels = [Action(g, g.ids.BET), Action(g, g.ids.CHECK)]
        node_label_suffix = "{}'s Decision Node".format(player.label)
        create_action_node(g, node, player, bet_round, action_labels, node_label_suffix, action, specific_actions, actions_so_far)

    ###############################################
    ########## CREATE ROW 2 AND BRANCHES ##########
    ###############################################

    # we are interested in just the first action, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:1]:
        specific_actions_so_far += specific_action

    # at the end of player 1's betting branch, 
    #   we need to create player 2's choice node that has raising, calling, and a folding branches
    actions_so_far = g.action_round_paths[1]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(root, 0)
        player = p2
        # action_labels = ["{}. {} raises", "{}. {} calls", "{}. {} folds"]
        action_labels = [Action(g, g.ids.RAISE), Action(g, g.ids.CALL), Action(g, g.ids.FOLD)]
        node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
        create_action_node(g, node, player, bet_round, action_labels, node_label_suffix, action, specific_actions, actions_so_far)

    # at the end of player 1's checking branch, 
    #   we need to create player 2's choice node that has raising and checking branches
    actions_so_far = g.action_round_paths[2]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(root, 1)
        player = p2
        # action_labels = ["{}. {} bets", "{}. {} checks"]
        action_labels = [Action(g, g.ids.BET), Action(g, g.ids.CHECK)]
        node_label_suffix = "{}'s Response Node given {} Checks".format(player.label, node.parent.player.label)
        create_action_node(g, node, player, bet_round, action_labels, node_label_suffix, action, specific_actions, actions_so_far)

    ###############################################
    ########## CREATE ROW 3 AND BRANCHES ##########
    ###############################################

    # we are interested in just the first two actions, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:2]:
        specific_actions_so_far += specific_action

    # at the end of player 2's raising branch, 
    #   we need to create player 1's choice node that has calling and folding branches
    actions_so_far = g.action_round_paths[3]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(root,0), 0)
        player = p1
        # action_labels = ["{}. {} calls", "{}. {} folds"]
        action_labels = [Action(g, g.ids.CALL), Action(g, g.ids.FOLD)]
        node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
        create_action_node(g, node, player, bet_round, action_labels, node_label_suffix, action, specific_actions, actions_so_far)

    # at the end of player 2's calling branch, 
    #   we need to create the chance branch
    actions_so_far = g.action_round_paths[4]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(root,0), 1)
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 1*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(g, node, bet_round, stop, action, bets)    

    # at the end of player 2's folding branch, 
    #   we need to create the terminal outcome branch
    actions_so_far = g.action_round_paths[5]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(root,0), 2)
        player = p1
        node_label_suffix = "{} folds".format(player.label)
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 0*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_terminal_node(g, node, bet_round, node_label_suffix, action, bets)  

    # at the end of player 2's betting branch, 
    #   we need to create player 1's choice node that has calling and folding branches
    actions_so_far = g.action_round_paths[6]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(root,1), 0)
        player = p1
        # action_labels = ["{}. {} calls", "{}. {} folds"]
        action_labels = [Action(g, g.ids.CALL), Action(g, g.ids.FOLD)]
        node_label_suffix = "{}'s Response Node given {} Bets".format(player.label, node.parent.player.label)
        create_action_node(g, node, player, bet_round, action_labels, node_label_suffix, action, specific_actions, actions_so_far)

    # at the end of player 2's checking branch, 
    #   we need to create a cst or terminal node
    actions_so_far = g.action_round_paths[7]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(root,1), 1)
        # bets = get_bets(pot/2 + 0*g.BET, pot/2 + 0*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(g, node, bet_round, stop, action, bets)

    ###############################################
    ########## CREATE ROW 4 AND BRANCHES ##########
    ###############################################

    # we are interested in all three actions, as a list
    specific_actions_so_far = ""
    for specific_action in specific_actions[:]:
        specific_actions_so_far += specific_action

    # at the end of player 1's calling branch, 
    #   we need to create a cst or terminal node
    actions_so_far = g.action_round_paths[8]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(get_child(root, 0), 0), 0)
        # bets = get_bets(pot/2 + 2*g.BET, pot/2 + 2*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(g, node, bet_round, stop, action, bets) 

    # at the end of player 1's folding branch, 
    #   we need to create a terminal node
    actions_so_far = g.action_round_paths[9]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(get_child(root, 0), 0), 1)
        player = p1
        node_label_suffix = "{} folds".format(player.label)
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 2*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_terminal_node(g, node, bet_round, node_label_suffix, action, bets)  

    # at the end of player 1's calling branch, 
    #   we need to create a cst or terminal node
    actions_so_far = g.action_round_paths[10]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(get_child(root, 1), 0), 0)
        # bets = get_bets(pot/2 + 1*g.BET, pot/2 + 1*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_chance_or_terminal_node(g, node, bet_round, stop, action, bets) 

    # at the end of player 1's folding branch, 
    #   we need to create a terminal node
    actions_so_far = g.action_round_paths[11]
    if actions_so_far.startswith(specific_actions_so_far):
        action = actions_so_far[-1]
        node = get_child(get_child(get_child(root, 1), 0), 1)
        player = p1
        node_label_suffix = "{} folds".format(player.label)
        # bets = get_bets(pot/2 + 0*g.BET, pot/2 + 1*g.BET) 
        bets = get_bets(g, pot, actions_so_far, bet_round)
        create_terminal_node(g, node, bet_round, node_label_suffix, action, bets)   


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


def create_terminal_node(g, node, bet_round, node_label_suffix, action, bets):
    
    node_label_suffix = "Terminal node. {}".format(node_label_suffix)
    node.label = set_node_label(g, node, bet_round, node_label_suffix, True, action, bets)


def create_chance_or_terminal_node(g, node, bet_round, stop, action, bets):

    if stop:
        node_label_suffix = "No More Rounds."
        create_terminal_node(g, node, bet_round, node_label_suffix, action, bets)
    else:
        pot = bets[0] + bets[1]
        create_cst(g, node, 0, bet_round+1, pot, action)


def create_action_node(g, node, player, bet_round, subtree_actions, node_label_suffix, action, specific_actions, actions_so_far):
    # specific_actions | actions_so_far | number_branches
    #       ""         |      ""        |       ALL
    #       ""         |      "B"       |       ALL
    #       "B"        |      ""        |        1       (only go down Bet route)
    #       "B"        |      "B"       |       ALL 
    
    ###########################################################################
    ############################ GET KEY TO INFOSET ###########################
    ###########################################################################

    # get infoset_mapping_key
    key = ""

    temp_node = node

    # if we specified we want short labels
    if g.SHORT_LABELS:
        
        # until we reach the root node...
        while temp_node != g.tree.root:
            
            temp_node = temp_node.parent
            # temp_player = temp_node.player.label
            # temp_label  = temp_node.label

            # unless it's not a chance node...
            # if (temp_node.player != g.tree.players.chance):

            # we want to keep adding the parents label
            key = temp_node.label + key

    
    # otherwise...
    else:

        # the parent's id    
        parent_id = node.parent.label.split()[0]

        # split up the tuple
        parts = parent_id.split("-")
        for part in parts:

            # don't include CHANCE mentions
            # also, the last part contains only the players name
            # and not the action, so we can't use it
            if part[0] != g.ids.CHANCE and len(part) > 1:
                key += part[1]
        
    # add the current action as well   
    key = key + action 

    ###########################################################################
    ########################## SOME BOOLEANS WE NEED ##########################
    ###########################################################################

    # the player specified is the current player 
    # for whom we're creating the node...
    is_focus_player = (player == g.PLAYER)

    # if the key is in our infoset_mapping...
    key_in_infoset_mapping = (key in g.infoset_mapping)

    # we need to know if we're creating just 1 action branch
    create_one_branch = (len(specific_actions) > len(actions_so_far))

    ###########################################################################
    ######################### ADD TO INFORMATION SET ##########################
    ###########################################################################

    if is_focus_player and key_in_infoset_mapping:

        # then we just need to add this node to its corresponding infoset
        # there is always only one infoset
        iset = g.infoset_mapping[key][0]
        # index = g.infoset_mapping[key]
        # iset = player.infosets[index]
        node.append_move(iset)

    ###########################################################################
    ####################### CREATE NEW INFORMATION SET ########################
    ###########################################################################

    # otherwise, we need to add the infoset
    else: 

        # we need to know if we're creating just 1 action branch
        if create_one_branch:
            n_actions = 1

        # ... or all action branches
        else:
            n_actions = len(subtree_actions)

        # create the action branch(es)
        index = len(player.infosets)
        iset = node.append_move(player, n_actions)
        iset.label = "Bet Round ({}) - {}".format(bet_round, key)

        # we need to add this infoset to to g.infoset_mapping...
        if key_in_infoset_mapping:
            # g.infoset_mapping[key] = index
            g.infoset_mapping[key].append(iset)
        else:
            g.infoset_mapping[key] = [iset]

        #######################################################################
        ######################### LABEL EACH ACTION ###########################
        #######################################################################
            
        # if we created just 1 action branch
        if create_one_branch:

            # get the action identifier that will tell us which action we need for this branch
            action_identifier = specific_actions[len(actions_so_far)]
            for subtree_action_index in range(len(subtree_actions)):
                subtree_action = subtree_actions[subtree_action_index]
                if subtree_action.get_identifier() == action_identifier:
                    
                    # set the action label
                    iset.actions[0].label = subtree_action.get_template(subtree_action_index, player)
                    break
        
        # ... or if we created all action branches
        else:

            for i in range(n_actions):
                subtree_action = subtree_actions[i]

                # set the action label
                iset.actions[i].label = subtree_action.get_template(i, player)

    #######################################################################
    ########################### LABEL THE NODE ############################
    #######################################################################

    # label player's choice node
    node.label = set_node_label(g, node, bet_round, node_label_suffix, False, action)


def set_node_label_chance(g, node, bet_round, pot, NODE_DESCRIPTION, is_terminal):
    '''
    This function just calls set_node_label, but with the action being empty.
    '''

    return set_node_label(g, node, bet_round, (pot/2,pot/2), NODE_DESCRIPTION, is_terminal, NO_ACTION)


def set_node_label(g, node, bet_round, NODE_DESCRIPTION, is_terminal, action, bets=(0,0)):
    '''
    Should return labels of the form: UNIQUE_ID - NODE_DESCRIPTION
    '''

    # we want a copy of the winner
    scenario_winner = g.winner

    # if the node is the root node, just return the n
    root = g.tree.root

    if node == root:
        UNIQUE_ID = g.ids.CHANCE

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
        # also, if there is a winner and they folded...
        if (bet_round == 1) or \
           (scenario_winner is not None and scenario_winner == folder):

            # set scenario_winner to be the non-folder
            scenario_winner = set_other_player(g, folder)

        # second, need to see how much they win
        amount = get_amount(scenario_winner, bets)

        # third, we get the outcome
        outcome = g.get_outcome(scenario_winner, amount)

        # finally, we set the outcome
        node.outcome = outcome

    else:
        raise Exception("I have no idea what player this is: {}".format(player))

    # if we specified we want short labels
    if g.SHORT_LABELS:
        
        # the label should just be the action itself
        label = action

    # otherwise, we need to create the label by looking at the parent node
    else:
        
        if node != root:

            # get child_index for node-labelling purposes
            child_index = node.prior_action.label.split(".")[0]

            # get the parent's unique identifier 
            # C0-A0-B - Colin's Response Node given Rose Bet
            # returns: C0-A0-B
            UNIQUE_ID_PARENT = node.parent.label.split()[0]

            # given C0-A0-B, we might want to create the new id C0-A0-B0-T = UNIQUE_ID_PARENT + 0-T
            UNIQUE_ID = "{}{}{}-{}".format(UNIQUE_ID_PARENT, action, child_index, player_id)

        # this is the label we'd like to return
        card_class = "{} has a {} and {} has a {}".format(g.tree.players[0].label, 
                                                          g.player1_class, 
                                                          g.tree.players[1].label, 
                                                          g.player2_class)
        
        # set the label to be a combination of the node's id and card classes witnessed
        # label = "{} - {}".format(UNIQUE_ID, card_class)
        label = "{}".format(UNIQUE_ID)

    return label


def set_other_player(g, player):
    '''
    Get the other player in the game.
    '''
    
    other_player = None

    if player == g.tree.players[0]:
        other_player = g.tree.players[1]
    else:
        other_player = g.tree.players[0]

    return other_player


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
        

def get_amount(winner, bets):
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
    # if   deal_size == 2 and repeat == 1 and bet_round == 1: decks_index = 0
    if   deal_size == 2 and repeat == 0 and bet_round == 1: decks_index = 1
    elif deal_size == 3 and repeat == 0 and bet_round == 2: decks_index = 2
    elif deal_size == 1 and repeat == 0 and bet_round == 3: decks_index = 3
    elif deal_size == 1 and repeat == 0 and bet_round == 4: decks_index = 4
    else: raise ValueError("Bad values for deal_size ({}), repeat ({}), and/or bet round ({})".format(deal_size, repeat, bet_round))
    return decks_index


def get_deck(g, bet_round):
    current_round = get_round(g, bet_round)
    deck = current_round.deck
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


# def compute_expected_values(g, s):

#     ###########################################################################
#     ################# Step 1: Get Infoset Mapping Key ################## 
#     ###########################################################################

#     # We first need to get all the actions that were specified in the
#     # configuration file

#     # the key we'll use in the g.infoset_mapping
#     key = ""

#     # get the rounds
#     rounds = g.rounds

#     # for each round
#     for _round in rounds:

#         # get the actions of that round
#         actions = _round.debug_actions

#         # for each action in those actions
#         for action in actions:

#             # add it to the key
#             key += action

#     # by this point we should have our key
    
#     ###########################################################################
#     ################# Step 2: Get Infoset  ################## 
#     ###########################################################################

#     # if the key is not in the info_set for some reason...
#     if key not in g.infoset_mapping:

#         # that's a problem
#         key_missing_template = "Oops, your key ({}) is not in the infoset."
#         key_missing = key_missing_template.format(key)
#         valid_keys_template = '''Valid infoset key-value pairs are:\n{}
#         Ensure your key corresponds to an action node owned by the player 
#         specified in the configuration file. Also, ensure it correspond to a 
#         valid node.'''
#         valid_keys = valid_keys_template.format(g.infoset_mapping.keys())
#         raise Exception("{} {}".format(key_missing, valid_keys))

#     # get the infoset stored in g.infoset_mapping
#     # THIS IS WRONG! NO NEED TO UPDATE IF THIS IS USELESS
#     iset = g.infoset_mapping[key]

#     common.print_expected_values(g, s, iset)


def create_restricted_tree(g):

    # create another 
    rg = create_game()

    # creates a new game tree with undominated strategies
    rg.tree = g.tree.support_profile().undominated().restrict()

    return rg


def prune_strictly_dominated_actions(g, s):
    '''
    Remove actions that are strictly dominated here.
    '''

    # we want to return a copy of the game 
    # pruned_game = create_game()
    # pruned_game.tree = deepcopy(g.tree)

    pruned_game = g

    # a list of lists of infosets in reverse-level order
    # get the keys
    keys = pruned_game.infoset_mapping.keys()
    keys.sort(key=len)
    keys.reverse()

    # the profile
    profile = pruned_game.tree.mixed_behavior_profile(rational=True)

    # n'th step index
    if s.PRINT_PRUNED_GAME_TREE_AFTER_EVERY_PRUNE:
        sub_process_index = 1
    
    for key_index in range(len(keys)):

        # for each level of infosets
        key = keys[key_index]
        isets = pruned_game.infoset_mapping[key]

        # for each infoset
        for iset_index in range(len(isets)):
        
            # get the infoset
            iset = isets[iset_index]

            # we want a list to store expected payoffs of each action
            expected_payoffs = []
        
            # for each action in an infoset
            for action in iset.actions:

                # get the expected payoff of performing this action
                expected_payoff = profile.payoff(action)
                
                # store the payoff
                expected_payoffs.append(expected_payoff)
                
            # get the maximum expected payoff
            max_expected_payoff = max(expected_payoffs)

            # indicator to keep track of an action getting deleted
            action_deleted = False

            # for each item in the list...
            for actions_index in range(len(iset.actions)-1, -1, -1):

                # if its expected value 
                if expected_payoffs[actions_index] < max_expected_payoff:
                    
                    # delete the action from the game
                    action = iset.actions[actions_index]
                    action.delete()

                    # update indicator
                    action_deleted = True

            # print the tree if necessary
            if s.PRINT_PRUNED_GAME_TREE_AFTER_EVERY_PRUNE and action_deleted:
                sub_process_string = "5.{}".format(sub_process_index)
                new_file_name = "{}-Part-{}".format(s.PRUNED_GAME_TREE_FILE, format(sub_process_index, '02'))   
                compute_time_of(sub_process_string, "Printing Pruned Game Tree", common.print_game, (pruned_game, s, new_file_name))
                sub_process_index += 1

            # reset indicator
            action_deleted = False

    return pruned_game


if __name__ == '__main__':

    # create the saver object
    s = compute_time_of(0, "Creating Saver", common.create_saver, ())

    # create the game object
    original_game = compute_time_of(1, "Creating Game", create_game, ())

    # if we want to debug our code, this is where we do it
    if original_game.DEBUG:
        import pudb; pu.db

    # game to solve
    game_to_solve = original_game

    try:

        # create the tree
        compute_time_of(2, "Creating Game Tree", create_tree, (original_game,))

        # print the original game
        if s.PRINT_ORIGINAL_GAME_TREE:
            compute_time_of(3, "Printing Original Game Tree", common.print_game, (original_game, s, s.ORIGINAL_GAME_TREE_FILE))
      
        # prune strictly dominated actions and print the game
        if s.PRINT_PRUNED_GAME_TREE:
            pruned_game = compute_time_of(4, "Pruning Game Tree", prune_strictly_dominated_actions, (original_game, s))
            game_to_solve = pruned_game
            compute_time_of(5, "Printing Pruned Game Tree", common.print_game, (pruned_game, s, s.PRUNED_GAME_TREE_FILE))

        # create and print the restricted game
        if s.PRINT_UNDOMINATED_GAME_MATRIX:
            restricted_game = compute_time_of(6, "Creating Restricted Matrix Game", create_restricted_tree, (pruned_game,))
            game_to_solve = restricted_game
            compute_time_of(7, "Printing Restricted Game", common.print_game, (restricted_game, s, s.REDUCED_GAME_TREE_FILE))
            
        # solve the most reduced game and print the solutions to a file
        if s.SOLVE_GAME:
            solutions = compute_time_of(8, "Solving Game", common.solve_game, (game_to_solve,))
            compute_time_of(9, "Printing Solutions", common.print_solutions, (solutions, s)) 

    except (KeyboardInterrupt):
        pass

    # print the expected values (to remove)
    # compute_time_of(7, "Computing Expected Values", compute_expected_values, (original_game, s))
