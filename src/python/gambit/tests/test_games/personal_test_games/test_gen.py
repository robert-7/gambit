import gambit
from fractions import Fraction
from nose.tools import assert_raises
from gambit.lib.error import UndefinedOperationError
import gen

class TestGen(object):

    def test_checks(self):
        "Test to ensure that checks returns the right value"
        s = "000"
        assert gen.checks(s, 0) == True
        assert gen.checks(s, 1) == True
        assert gen.checks(s, 2) == True

        s = "1111"
        assert gen.checks(s, 0) == False
        assert gen.checks(s, 1) == False
        assert gen.checks(s, 2) == False
        assert gen.checks(s, 3) == False

        s = "100111"
        assert gen.checks(s, 0) == False
        assert gen.checks(s, 1) == False
        assert gen.checks(s, 2) == False
        assert gen.checks(s, 3) == True
        assert gen.checks(s, 4) == True
        assert gen.checks(s, 5) == False

    def test_bets(self):
        "Test to ensure that bets returns the right value"
        s = "000"
        assert gen.bets(s, 0) == False
        assert gen.bets(s, 1) == False
        assert gen.bets(s, 2) == False

        s = "1111"
        assert gen.bets(s, 0) == True
        assert gen.bets(s, 1) == True
        assert gen.bets(s, 2) == True
        assert gen.bets(s, 3) == True

        s = "100111"
        assert gen.bets(s, 0) == True
        assert gen.bets(s, 1) == True
        assert gen.bets(s, 2) == True
        assert gen.bets(s, 3) == False
        assert gen.bets(s, 4) == False
        assert gen.bets(s, 5) == True

    def test_folds(self):
        "Test to ensure that folds returns the right value"
        s = "000"
        assert gen.folds(s, 0) == True
        assert gen.folds(s, 1) == True
        assert gen.folds(s, 2) == True

        s = "1111"
        assert gen.folds(s, 0) == False
        assert gen.folds(s, 1) == False
        assert gen.folds(s, 2) == False
        assert gen.folds(s, 3) == False

        s = "100111"
        assert gen.folds(s, 0) == False
        assert gen.folds(s, 1) == False
        assert gen.folds(s, 2) == False
        assert gen.folds(s, 3) == True
        assert gen.folds(s, 4) == True
        assert gen.folds(s, 5) == False

    def test_calls(self):
        "Test to ensure that calls returns the right value"
        s = "000"
        assert gen.calls(s, 0) == False
        assert gen.calls(s, 1) == False
        assert gen.calls(s, 2) == False

        s = "1111"
        assert gen.calls(s, 0) == True
        assert gen.calls(s, 1) == True
        assert gen.calls(s, 2) == True
        assert gen.calls(s, 3) == True

        s = "100111"
        assert gen.calls(s, 0) == True
        assert gen.calls(s, 1) == True
        assert gen.calls(s, 2) == True
        assert gen.calls(s, 3) == False
        assert gen.calls(s, 4) == False
        assert gen.calls(s, 5) == True

    def test_calculate_payoffs(self):
        ante = 1
        bet = 2

        s0 = "001"
        s1 = "000"

        i = 0
        j = 1
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        i = 0
        j = 2
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)
        
        i = 1
        j = 0
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        i = 1
        j = 2
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (-1, 1)

        i = 2
        j = 0
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        i = 2
        j = 1
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        s0 = "010"
        s1 = "011"

        i = 0
        j = 1
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (-1, 1)

        i = 0
        j = 2
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (-1, 1)
        
        i = 1
        j = 0
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (3, -3)

        i = 1
        j = 2
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        i = 2
        j = 0
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        i = 2
        j = 1
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        s0 = "010"
        s1 = "101"

        i = 0
        j = 1
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (-1, 1)

        i = 0
        j = 2
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (-1, 1)
        
        i = 1
        j = 0
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (3, -3)

        i = 1
        j = 2
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (-3, 3)

        i = 2
        j = 0
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

        i = 2
        j = 1
        assert gen.calculate_payoffs(s0, s1, i, j, ante, bet) == (1, -1)

    def test_expected_payoffs(self):
        ante = 1
        bet = 2
        num_cards = 3

        s0 = "010"
        s1 = "011"

        assert gen.expected_payoffs(s0, s1, ante, bet, num_cards) == (Fraction(4, 6), Fraction(-4,6))

        s0 = "010"
        s1 = "101"

        assert gen.expected_payoffs(s0, s1, ante, bet, num_cards) == (0, 0)

if __name__ == "__main__":
    test = TestGen()
    test.test_checks()
    test.test_bets()
    test.test_folds()
    test.test_calls()
    test.test_calculate_payoffs()
    test.test_expected_payoffs()