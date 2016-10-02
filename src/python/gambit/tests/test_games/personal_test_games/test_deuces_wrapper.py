import gambit
from fractions import Fraction
from nose.tools import assert_raises
from gambit.lib.error import UndefinedOperationError
from deuces_wrapper import *

class TestGen(object):

    def test_adjust_rank(self, old_card_rank, class_rank, new_card_rank):
        "Test to ensure that adjust_rank returns the right rank"
        assert adjust_rank(old_card_rank, class_rank) == new_card_rank

    def test_return_winner(self, old_card_rank, class_rank, new_card_rank):
        "Test to ensure that adjust_rank returns the right rank"
        assert adjust_rank(old_card_rank, class_rank) == new_card_rank


if __name__ == "__main__":
    test = TestGen()

    # test we're adjusting the card ranks correctly
    test.test_adjust_rank(1, 1, 1)
    test.test_adjust_rank(10, 1, 10)
    test.test_adjust_rank(11, 2, 11)
    test.test_adjust_rank(166, 2, 166)
    test.test_adjust_rank(167, 3, 167+1277)
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
    test.test_adjust_rank(2649, 7, 2649)

    # test.test_bets()
    # test.test_folds()
    # test.test_calls()
    # test.test_calculate_payoffs()
    # test.test_expected_payoffs()

