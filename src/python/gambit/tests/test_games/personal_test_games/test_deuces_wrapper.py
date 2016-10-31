import gambit
from fractions import Fraction
from nose.tools import assert_raises
from gambit.lib.error import UndefinedOperationError
import unittest
import deuces
from deuces_wrapper import *
import gen_tree_manila_poker

class TestGen(unittest.TestCase):

    def setUp(self):
        # test = TestGen()
        # testing whether we're returning the correct winner
        self.g = gen_tree_manila_poker.Poker(MIXED_STRATEGIES=True,
                                             ANTE=1, 
                                             BET=2, 
                                             RAISE=2,
                                             ACE_WRAPS=True,
                                             LOWEST_CARD=2, 
                                             HIGHEST_CARD=14, 
                                             NUMBER_OF_SUITS=4,
                                             NUMBER_OF_ROUNDS=4,
                                             DEBUG=True)
        self.g.tree = gambit.Game.new_tree()
        self.g.tree.players.add("Rose")
        self.g.tree.players.add("Colin")
        self.g.DEBUG = True
        self.g.mpm = Manila_Poker_Mapping()
    
    def tearDown(self):
        pass

    def test_adjust_rank(self):
        "Test to ensure that adjust_rank returns the right rank"
        
        # testing whether we're adjusting the card ranks correctly

        # return the same value
        assert adjust_rank(1,    1) == 1          # Ace-High Straight flush 
        assert adjust_rank(10,   1) == 10         # 5-High Straight flush
        assert adjust_rank(11,   2) == 11         # Quad Aces, King Kicker
        assert adjust_rank(166,  2) == 166        # 

        # return modified values
        assert adjust_rank(167,  3) == 167+1277   # Full House, Aces over Kings
        assert adjust_rank(200,  3) == 200+1277
        assert adjust_rank(322,  3) == 322+1277
        assert adjust_rank(323,  4) == 323-156
        assert adjust_rank(1000, 4) == 1000-156
        assert adjust_rank(1599, 4) == 1599-156
        assert adjust_rank(1600, 5) == 1600
        assert adjust_rank(1605, 5) == 1605
        assert adjust_rank(1610, 5) == 1610
        assert adjust_rank(1611, 6) == 1611
        assert adjust_rank(2000, 6) == 2000
        assert adjust_rank(2648, 6) == 2648

        # # return the same value
        assert adjust_rank(2649, 7) == 2649


    def test_return_winner(self):
        "Test to ensure that return_winner returns the right winner"

        # should raise error since 5 of hearts is not allowed in a deck with 6s and higher
        assert_raises(ValueError, 
                      self._test_return_winner, 
                      cards_in_play=["5h", "7h"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"], 
                      ACE_WRAPS = True,
                      LOWEST_CARD=6, 
                      NUMBER_OF_SUITS=4, 
                      player=self.g.tree.players[0])

        # straight flush winner
        self._test_return_winner(cards_in_play=["6h", "7h"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=2, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        self._test_return_winner(cards_in_play=["6h", "7h"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        # both have straights so it's a tie
        self._test_return_winner(cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=2, 
                                 NUMBER_OF_SUITS=4, 
                                 player=None)

        self._test_return_winner(cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=None)

        # both have the 3 of a kind 
        self._test_return_winner(cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=2, 
                                 NUMBER_OF_SUITS=4, 
                                 player=None)

        self._test_return_winner(cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=None)

        # both have the 3 of a kind, though player 2's is stronger
        self._test_return_winner(cards_in_play=["6h", "Ad"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=2, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        self._test_return_winner(cards_in_play=["6h", "Ad"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        # player 1 has a straight, while player 2 has a 3 of a kind... 
        # depending on the lowest card in the deck, player 1 or player 2 should win
        self._test_return_winner(cards_in_play=["8h", "9d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=2, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        self._test_return_winner(cards_in_play=["8h", "9d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        # player 1 has a full house, while player 2 has a flush... 
        # depending on the lowest card in the deck, player 1 or player 2 should win
        self._test_return_winner(cards_in_play=["6h", "7d"] + ["6c", "9c"] + ["6s", "6d", "7c", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=2, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[0])

        self._test_return_winner(cards_in_play=["6h", "7d"] + ["6c", "9c"] + ["6s", "6d", "7c", "Jc", "Qc"], 
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[1])

        # player 1 should not have a straight-flush since the lowest card does not allow him to have a straight
        self._test_return_winner(cards_in_play=["Ah", "Jc"] + ["Th", "8c"] + ["6h", "7h", "8h", "9h", "8s"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=5, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[1])

        # player 2 is still a straight flush winner due to Ace Wrap having one less value than 6-10 straight
        self._test_return_winner(cards_in_play=["Ah", "Jc"] + ["Th", "8c"] + ["6h", "7h", "8h", "9h", "8s"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[1])

        # player 2 is still a straight flush winner due to Ace Wrap having one less value than 6-10 straight
        self._test_return_winner(cards_in_play=["Ah", "Ad"] + ["6c", "Th"] + ["6h", "7h", "8h", "9h", "6d"],  
                                 ACE_WRAPS = True,
                                 LOWEST_CARD=6, 
                                 NUMBER_OF_SUITS=4, 
                                 player=self.g.tree.players[1])


    def _test_return_winner(self, cards_in_play, ACE_WRAPS, LOWEST_CARD, NUMBER_OF_SUITS, player):
        "Test to ensure that return_winner returns the right winner"

        self.g.cards_in_play = cards_in_play
        self.g.ACE_WRAPS = ACE_WRAPS
        self.g.LOWEST_CARD = LOWEST_CARD
        self.g.NUMBER_OF_SUITS = NUMBER_OF_SUITS
        
        # we need to indicate what bet round it is:
        if len(cards_in_play) == 9:
            bet_round = 4
        elif len(cards_in_play) == 8:
            bet_round = 3
        elif len(cards_in_play) == 7:
            bet_round = 2
        else:
            error_msg = "Bad number of cards in play ({}). Should be one of: 7, 8, 9"
            raise Exception(error_msg.format(len(cards_in_play)))
        
        assert get_showdown_winner(self.g, bet_round) == player
