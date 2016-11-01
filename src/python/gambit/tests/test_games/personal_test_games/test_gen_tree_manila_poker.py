import gambit
from fractions import Fraction
from nose.tools import assert_raises
from gambit.lib.error import UndefinedOperationError
import unittest
import gen_tree_manila_poker as gtmp
from sys import argv

class TestGen(unittest.TestCase):

    def setUp(self):
        # test = TestGen()
        # testing whether we're returning the correct winner
        self.g = gtmp.Poker(MIXED_STRATEGIES=True,
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
    
    def tearDown(self):
        pass


    def test_get_bets(self):

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

        # get each action round path as a string
        ARPAS = []
        for arp in self.g.action_round_paths:
            ARPAS.append(''.join(arp))

        pot = 8
        bet_round = 2
        b = self.g.BET
        r = self.g.RAISE
        self._test_get_bets(pot, ARPAS[4],  bet_round, (pot/2 + 1*b, pot/2 + 1*b)) # BK
        self._test_get_bets(pot, ARPAS[5],  bet_round, (pot/2 + 1*b, pot/2 + 0*b)) # BF
        self._test_get_bets(pot, ARPAS[7],  bet_round, (pot/2 + 0*b, pot/2 + 0*b)) # CC
        self._test_get_bets(pot, ARPAS[8],  bet_round, (pot/2 + 2*b, pot/2 + 2*b)) # BRK
        self._test_get_bets(pot, ARPAS[9],  bet_round, (pot/2 + 1*b, pot/2 + 2*b)) # BRF
        self._test_get_bets(pot, ARPAS[10], bet_round, (pot/2 + 1*b, pot/2 + 1*b)) # CBK
        self._test_get_bets(pot, ARPAS[11], bet_round, (pot/2 + 0*b, pot/2 + 1*b)) # CBF
        

    def _test_get_bets(self, pot, arpas, bet_round, correct_answer):
        solution = gtmp.get_bets(self.g, pot, arpas, bet_round)
        print(arpas + " " + str(solution))
        assert solution == correct_answer


    def test_get_order(self):
        "Test to ensure that get_order returns the right order"
        
        # test 2 cards
        self._test_helper(function=gtmp.get_order, cards=[0,1], MAX=5, order=0)
        self._test_helper(function=gtmp.get_order, cards=[0,2], MAX=5, order=1)
        self._test_helper(function=gtmp.get_order, cards=[0,3], MAX=5, order=2)
        self._test_helper(function=gtmp.get_order, cards=[0,4], MAX=5, order=3)
        self._test_helper(function=gtmp.get_order, cards=[1,2], MAX=5, order=4)
        self._test_helper(function=gtmp.get_order, cards=[1,3], MAX=5, order=5)
        self._test_helper(function=gtmp.get_order, cards=[1,4], MAX=5, order=6)
        self._test_helper(function=gtmp.get_order, cards=[2,3], MAX=5, order=7)
        self._test_helper(function=gtmp.get_order, cards=[2,4], MAX=5, order=8)
        self._test_helper(function=gtmp.get_order, cards=[3,4], MAX=5, order=9)

        self._test_helper(function=gtmp.get_order, cards=[0,1], MAX=6, order=0)
        self._test_helper(function=gtmp.get_order, cards=[0,2], MAX=6, order=1)
        self._test_helper(function=gtmp.get_order, cards=[0,3], MAX=6, order=2)
        self._test_helper(function=gtmp.get_order, cards=[0,4], MAX=6, order=3)
        self._test_helper(function=gtmp.get_order, cards=[0,5], MAX=6, order=4)
        self._test_helper(function=gtmp.get_order, cards=[1,2], MAX=6, order=5)
        self._test_helper(function=gtmp.get_order, cards=[1,3], MAX=6, order=6)
        self._test_helper(function=gtmp.get_order, cards=[1,4], MAX=6, order=7)
        self._test_helper(function=gtmp.get_order, cards=[1,5], MAX=6, order=8)
        self._test_helper(function=gtmp.get_order, cards=[2,3], MAX=6, order=9)
        self._test_helper(function=gtmp.get_order, cards=[2,4], MAX=6, order=10)
        self._test_helper(function=gtmp.get_order, cards=[2,5], MAX=6, order=11)
        self._test_helper(function=gtmp.get_order, cards=[3,4], MAX=6, order=12)
        self._test_helper(function=gtmp.get_order, cards=[3,5], MAX=6, order=13)
        self._test_helper(function=gtmp.get_order, cards=[4,5], MAX=6, order=14)

        # test 3 cards
        self._test_helper(function=gtmp.get_order, cards=[0,1,2], MAX=5, order=0)
        self._test_helper(function=gtmp.get_order, cards=[0,1,3], MAX=5, order=1)
        self._test_helper(function=gtmp.get_order, cards=[0,1,4], MAX=5, order=2)
        self._test_helper(function=gtmp.get_order, cards=[0,2,3], MAX=5, order=3)
        self._test_helper(function=gtmp.get_order, cards=[0,2,4], MAX=5, order=4)
        self._test_helper(function=gtmp.get_order, cards=[0,3,4], MAX=5, order=5)
        self._test_helper(function=gtmp.get_order, cards=[1,2,3], MAX=5, order=6)
        self._test_helper(function=gtmp.get_order, cards=[1,2,4], MAX=5, order=7)
        self._test_helper(function=gtmp.get_order, cards=[1,3,4], MAX=5, order=8)
        self._test_helper(function=gtmp.get_order, cards=[2,3,4], MAX=5, order=9)

        self._test_helper(function=gtmp.get_order, cards=[0,1,2], MAX=6, order=0)
        self._test_helper(function=gtmp.get_order, cards=[0,1,3], MAX=6, order=1)
        self._test_helper(function=gtmp.get_order, cards=[0,1,4], MAX=6, order=2)
        self._test_helper(function=gtmp.get_order, cards=[0,1,5], MAX=6, order=3)
        self._test_helper(function=gtmp.get_order, cards=[0,2,3], MAX=6, order=4)
        self._test_helper(function=gtmp.get_order, cards=[0,2,4], MAX=6, order=5)
        self._test_helper(function=gtmp.get_order, cards=[0,2,5], MAX=6, order=6)
        self._test_helper(function=gtmp.get_order, cards=[0,3,4], MAX=6, order=7)
        self._test_helper(function=gtmp.get_order, cards=[0,3,5], MAX=6, order=8)
        self._test_helper(function=gtmp.get_order, cards=[0,4,5], MAX=6, order=9)
        self._test_helper(function=gtmp.get_order, cards=[1,2,3], MAX=6, order=10)
        self._test_helper(function=gtmp.get_order, cards=[1,2,4], MAX=6, order=11)
        self._test_helper(function=gtmp.get_order, cards=[1,2,5], MAX=6, order=12)
        self._test_helper(function=gtmp.get_order, cards=[1,3,4], MAX=6, order=13)
        self._test_helper(function=gtmp.get_order, cards=[1,3,5], MAX=6, order=14)
        self._test_helper(function=gtmp.get_order, cards=[1,4,5], MAX=6, order=15)
        self._test_helper(function=gtmp.get_order, cards=[2,3,4], MAX=6, order=16)
        self._test_helper(function=gtmp.get_order, cards=[2,3,5], MAX=6, order=17)
        self._test_helper(function=gtmp.get_order, cards=[2,4,5], MAX=6, order=18)
        self._test_helper(function=gtmp.get_order, cards=[3,4,5], MAX=6, order=19)


    def test_get_order_hole(self):
        "Test to ensure that get_order returns the right order"
        
        # test 4 cards
        self._test_helper(function=gtmp.get_order_hole, cards=[0,1,2,3], MAX=5, order=[0])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,1,2,4], MAX=5, order=[1])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,1,3,4], MAX=5, order=[2])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,2,1,3], MAX=5, order=[3])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,2,1,4], MAX=5, order=[4])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,2,3,4], MAX=5, order=[5])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,3,1,2], MAX=5, order=[6])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,3,1,4], MAX=5, order=[7])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,3,2,4], MAX=5, order=[8])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,4,1,2], MAX=5, order=[9])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,4,1,3], MAX=5, order=[10])
        self._test_helper(function=gtmp.get_order_hole, cards=[0,4,2,3], MAX=5, order=[11])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,2,0,3], MAX=5, order=[12])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,2,0,4], MAX=5, order=[13])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,2,3,4], MAX=5, order=[14])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,3,0,2], MAX=5, order=[15])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,3,0,4], MAX=5, order=[16])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,3,2,4], MAX=5, order=[17])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,4,0,2], MAX=5, order=[18])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,4,0,3], MAX=5, order=[19])
        self._test_helper(function=gtmp.get_order_hole, cards=[1,4,2,3], MAX=5, order=[20])
        self._test_helper(function=gtmp.get_order_hole, cards=[2,3,0,1], MAX=5, order=[21])
        self._test_helper(function=gtmp.get_order_hole, cards=[2,3,0,4], MAX=5, order=[22])
        self._test_helper(function=gtmp.get_order_hole, cards=[2,3,1,4], MAX=5, order=[23])
        self._test_helper(function=gtmp.get_order_hole, cards=[2,4,0,1], MAX=5, order=[24])
        self._test_helper(function=gtmp.get_order_hole, cards=[2,4,0,3], MAX=5, order=[25])
        self._test_helper(function=gtmp.get_order_hole, cards=[2,4,1,3], MAX=5, order=[26])
        self._test_helper(function=gtmp.get_order_hole, cards=[3,4,0,1], MAX=5, order=[27])
        self._test_helper(function=gtmp.get_order_hole, cards=[3,4,0,2], MAX=5, order=[28])
        self._test_helper(function=gtmp.get_order_hole, cards=[3,4,1,2], MAX=5, order=[29])


    def test_get_order_hole_flop(self):
        "Test to ensure that get_order_hole_flop returns the right order"
        
        # test 7 cards
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,3,4,5,6], MAX=8, order=[0,0])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,3,4,5,7], MAX=8, order=[0,1])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,3,4,6,7], MAX=8, order=[0,2])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,3,5,6,7], MAX=8, order=[0,3])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,4,3,5,6], MAX=8, order=[1,0])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,4,3,5,7], MAX=8, order=[1,1])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,4,3,6,7], MAX=8, order=[1,2])
        self._test_helper(function=gtmp.get_order_hole_flop, cards=[0,1,2,4,5,6,7], MAX=8, order=[1,3])


    def _test_helper(self, function, cards, MAX, order):
        "Test to ensure that get_order_hole_flop returns the right order"
        
        solution = function(cards, MAX)
        assert solution == order

if __name__ == "__main__":
    if len(argv) == 2 and argv[1] == "--debug":
        import pudb; pu.db
    
    # put function below
