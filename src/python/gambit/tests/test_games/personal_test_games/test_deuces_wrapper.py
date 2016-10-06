import gambit
from fractions import Fraction
from nose.tools import assert_raises
from gambit.lib.error import UndefinedOperationError
import deuces
from deuces_wrapper import *
import gen_tree_manila_poker

class TestGen(object):

    def test_adjust_rank(self, old_card_rank, class_rank, new_card_rank):
        "Test to ensure that adjust_rank returns the right rank"
        
        assert adjust_rank(old_card_rank, class_rank) == new_card_rank

    def test_return_winner(self, g, cards_in_play, ACE_WRAPS, LOWEST_CARD, NUMBER_OF_SUITS, player):
        "Test to ensure that return_winner returns the right winner"

        g.cards_in_play = cards_in_play
        g.ACE_WRAPS = ACE_WRAPS
        g.LOWEST_CARD = LOWEST_CARD
        g.NUMBER_OF_SUITS = NUMBER_OF_SUITS
        assert return_winner(g) == player


if __name__ == "__main__":
    test = TestGen()

    # testing whether we're adjusting the card ranks correctly

    # return the same value
    test.test_adjust_rank(1, 1, 1)            # Ace-High Straight flush 
    test.test_adjust_rank(10, 1, 10)          # 5-High Straight flush
    test.test_adjust_rank(11, 2, 11)          # Quad Aces, King Kicker
    test.test_adjust_rank(166, 2, 166)        # 

    # return modified values
    test.test_adjust_rank(167, 3, 167+1277)   # Full House, Aces over Kings
    test.test_adjust_rank(200, 3, 200+1277)
    test.test_adjust_rank(322, 3, 322+1277)
    test.test_adjust_rank(323, 4, 323-156)
    test.test_adjust_rank(1000, 4, 1000-156)
    test.test_adjust_rank(1599, 4, 1599-156)
    test.test_adjust_rank(1600, 5, 1600+858)
    test.test_adjust_rank(1605, 5, 1605+858)
    test.test_adjust_rank(1610, 5, 1610+858)
    test.test_adjust_rank(1611, 6, 1611-10)
    test.test_adjust_rank(2000, 6, 2000-10)
    test.test_adjust_rank(2648, 6, 2648-10)

    # return the same value
    test.test_adjust_rank(2649, 7, 2649)

    # testing whether we're returning the correct winner
    g = gen_tree_manila_poker.Poker(MIXED_STRATEGIES=True,
                                    ANTE=1, 
                                    BET=2, 
                                    RAISE=2,
                                    ACE_WRAPS=True,
                                    LOWEST_CARD=2, 
                                    HIGHEST_CARD=14, 
                                    NUMBER_OF_SUITS=4)
    g.tree = gambit.Game.new_tree()
    g.tree.players.add("Rose")
    g.tree.players.add("Colin")
    g.DEBUG = True
    g.mpm = Manila_Poker_Mapping()

    # should raise error since 5 of hearts is not allowed in a deck with 6s and higher
    assert_raises(ValueError, 
                  test.test_return_winner, 
                  g=g, 
                  cards_in_play=["5h", "7h"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"], 
                  ACE_WRAPS = True,
                  LOWEST_CARD=6, 
                  NUMBER_OF_SUITS=4, 
                  player=g.tree.players[0])

    # straight flush winner
    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7h"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=2, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[0])

    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7h"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[0])

    # both have straights so it's a tie
    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=2, 
                            NUMBER_OF_SUITS=4, 
                            player=None)

    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["8h", "9h", "Th", "8c", "9c"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=None)

    # both have the 3 of a kind 
    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=2, 
                            NUMBER_OF_SUITS=4, 
                            player=None)

    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=None)

    # both have the 3 of a kind, though player 2's is stronger
    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "Ad"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=2, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[0])

    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "Ad"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[0])

    # player 1 has a straight, while player 2 has a 3 of a kind... 
    # depending on the lowest card in the deck, player 1 or player 2 should win
    test.test_return_winner(g=g, 
                            cards_in_play=["8h", "9d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=2, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[0])

    test.test_return_winner(g=g, 
                            cards_in_play=["8h", "9d"] + ["6c", "7c"] + ["6s", "6d", "Th", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[1])

    # player 1 has a full house, while player 2 has a flush... 
    # depending on the lowest card in the deck, player 1 or player 2 should win
    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7d"] + ["6c", "9c"] + ["6s", "6d", "7c", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=2, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[0])

    test.test_return_winner(g=g, 
                            cards_in_play=["6h", "7d"] + ["6c", "9c"] + ["6s", "6d", "7c", "Jc", "Qc"], 
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[1])

    # player 1 should not have a straight-flush since the lowest card does not allow him to have a straight
    test.test_return_winner(g=g, 
                            cards_in_play=["Ah", "Jc"] + ["Th", "8c"] + ["6h", "7h", "8h", "9h", "8s"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=5, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[1])

    # player 2 is still a straight flush winner due to Ace Wrap having one less value than 6-10 straight
    test.test_return_winner(g=g, 
                            cards_in_play=["Ah", "Jc"] + ["Th", "8c"] + ["6h", "7h", "8h", "9h", "8s"],  
                            ACE_WRAPS = True,
                            LOWEST_CARD=6, 
                            NUMBER_OF_SUITS=4, 
                            player=g.tree.players[1])