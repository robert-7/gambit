import gambit
from fractions import Fraction
from nose.tools import assert_raises
from gambit.lib.error import UndefinedOperationError
import gen_tree_manila_poker as gtmp
from sys import argv

class TestGen(object):

    def test_get_order(self, cards, MAX, order):
        "Test to ensure that get_order returns the right order"
        
        solution = gtmp.get_order(cards, MAX)
        assert solution == order

    def test_get_order_hole(self, cards, MAX, order):
        "Test to ensure that get_order returns the right order"
        
        solution = gtmp.get_order_hole(cards, MAX)
        assert solution == order

    def test_get_order_hole_flop(self, cards, MAX, order):
        "Test to ensure that get_order_hole_flop returns the right order"
        
        solution = gtmp.get_order_hole_flop(cards, MAX)
        assert solution == order

if __name__ == "__main__":
    test = TestGen()
    if len(argv) == 2 and argv[1] == "--debug":
        import pudb; pu.db

    # test 2 cards
    test.test_get_order(cards=[0,1], MAX=5, order=0)
    test.test_get_order(cards=[0,2], MAX=5, order=1)
    test.test_get_order(cards=[0,3], MAX=5, order=2)
    test.test_get_order(cards=[0,4], MAX=5, order=3)
    test.test_get_order(cards=[1,2], MAX=5, order=4)
    test.test_get_order(cards=[1,3], MAX=5, order=5)
    test.test_get_order(cards=[1,4], MAX=5, order=6)
    test.test_get_order(cards=[2,3], MAX=5, order=7)
    test.test_get_order(cards=[2,4], MAX=5, order=8)
    test.test_get_order(cards=[3,4], MAX=5, order=9)

    test.test_get_order(cards=[0,1], MAX=6, order=0)
    test.test_get_order(cards=[0,2], MAX=6, order=1)
    test.test_get_order(cards=[0,3], MAX=6, order=2)
    test.test_get_order(cards=[0,4], MAX=6, order=3)
    test.test_get_order(cards=[0,5], MAX=6, order=4)
    test.test_get_order(cards=[1,2], MAX=6, order=5)
    test.test_get_order(cards=[1,3], MAX=6, order=6)
    test.test_get_order(cards=[1,4], MAX=6, order=7)
    test.test_get_order(cards=[1,5], MAX=6, order=8)
    test.test_get_order(cards=[2,3], MAX=6, order=9)
    test.test_get_order(cards=[2,4], MAX=6, order=10)
    test.test_get_order(cards=[2,5], MAX=6, order=11)
    test.test_get_order(cards=[3,4], MAX=6, order=12)
    test.test_get_order(cards=[3,5], MAX=6, order=13)
    test.test_get_order(cards=[4,5], MAX=6, order=14)

    # test 3 cards
    test.test_get_order(cards=[0,1,2], MAX=5, order=0)
    test.test_get_order(cards=[0,1,3], MAX=5, order=1)
    test.test_get_order(cards=[0,1,4], MAX=5, order=2)
    test.test_get_order(cards=[0,2,3], MAX=5, order=3)
    test.test_get_order(cards=[0,2,4], MAX=5, order=4)
    test.test_get_order(cards=[0,3,4], MAX=5, order=5)
    test.test_get_order(cards=[1,2,3], MAX=5, order=6)
    test.test_get_order(cards=[1,2,4], MAX=5, order=7)
    test.test_get_order(cards=[1,3,4], MAX=5, order=8)
    test.test_get_order(cards=[2,3,4], MAX=5, order=9)

    test.test_get_order(cards=[0,1,2], MAX=6, order=0)
    test.test_get_order(cards=[0,1,3], MAX=6, order=1)
    test.test_get_order(cards=[0,1,4], MAX=6, order=2)
    test.test_get_order(cards=[0,1,5], MAX=6, order=3)
    test.test_get_order(cards=[0,2,3], MAX=6, order=4)
    test.test_get_order(cards=[0,2,4], MAX=6, order=5)
    test.test_get_order(cards=[0,2,5], MAX=6, order=6)
    test.test_get_order(cards=[0,3,4], MAX=6, order=7)
    test.test_get_order(cards=[0,3,5], MAX=6, order=8)
    test.test_get_order(cards=[0,4,5], MAX=6, order=9)
    test.test_get_order(cards=[1,2,3], MAX=6, order=10)
    test.test_get_order(cards=[1,2,4], MAX=6, order=11)
    test.test_get_order(cards=[1,2,5], MAX=6, order=12)
    test.test_get_order(cards=[1,3,4], MAX=6, order=13)
    test.test_get_order(cards=[1,3,5], MAX=6, order=14)
    test.test_get_order(cards=[1,4,5], MAX=6, order=15)
    test.test_get_order(cards=[2,3,4], MAX=6, order=16)
    test.test_get_order(cards=[2,3,5], MAX=6, order=17)
    test.test_get_order(cards=[2,4,5], MAX=6, order=18)
    test.test_get_order(cards=[3,4,5], MAX=6, order=19)

    # test 4 cards
    test.test_get_order_hole(cards=[0,1,2,3], MAX=5, order=[0])
    test.test_get_order_hole(cards=[0,1,2,4], MAX=5, order=[1])
    test.test_get_order_hole(cards=[0,1,3,4], MAX=5, order=[2])
    test.test_get_order_hole(cards=[0,2,1,3], MAX=5, order=[3])
    test.test_get_order_hole(cards=[0,2,1,4], MAX=5, order=[4])
    test.test_get_order_hole(cards=[0,2,3,4], MAX=5, order=[5])
    test.test_get_order_hole(cards=[0,3,1,2], MAX=5, order=[6])
    test.test_get_order_hole(cards=[0,3,1,4], MAX=5, order=[7])
    test.test_get_order_hole(cards=[0,3,2,4], MAX=5, order=[8])
    test.test_get_order_hole(cards=[0,4,1,2], MAX=5, order=[9])
    test.test_get_order_hole(cards=[0,4,1,3], MAX=5, order=[10])
    test.test_get_order_hole(cards=[0,4,2,3], MAX=5, order=[11])
    test.test_get_order_hole(cards=[1,2,0,3], MAX=5, order=[12])
    test.test_get_order_hole(cards=[1,2,0,4], MAX=5, order=[13])
    test.test_get_order_hole(cards=[1,2,3,4], MAX=5, order=[14])
    test.test_get_order_hole(cards=[1,3,0,2], MAX=5, order=[15])
    test.test_get_order_hole(cards=[1,3,0,4], MAX=5, order=[16])
    test.test_get_order_hole(cards=[1,3,2,4], MAX=5, order=[17])
    test.test_get_order_hole(cards=[1,4,0,2], MAX=5, order=[18])
    test.test_get_order_hole(cards=[1,4,0,3], MAX=5, order=[19])
    test.test_get_order_hole(cards=[1,4,2,3], MAX=5, order=[20])
    test.test_get_order_hole(cards=[2,3,0,1], MAX=5, order=[21])
    test.test_get_order_hole(cards=[2,3,0,4], MAX=5, order=[22])
    test.test_get_order_hole(cards=[2,3,1,4], MAX=5, order=[23])
    test.test_get_order_hole(cards=[2,4,0,1], MAX=5, order=[24])
    test.test_get_order_hole(cards=[2,4,0,3], MAX=5, order=[25])
    test.test_get_order_hole(cards=[2,4,1,3], MAX=5, order=[26])
    test.test_get_order_hole(cards=[3,4,0,1], MAX=5, order=[27])
    test.test_get_order_hole(cards=[3,4,0,2], MAX=5, order=[28])
    test.test_get_order_hole(cards=[3,4,1,2], MAX=5, order=[29])

    # test 7 cards
    test.test_get_order_hole_flop(cards=[0,1,2,3,4,5,6], MAX=8, order=[0,0])
    test.test_get_order_hole_flop(cards=[0,1,2,3,4,5,7], MAX=8, order=[0,1])
    test.test_get_order_hole_flop(cards=[0,1,2,3,4,6,7], MAX=8, order=[0,2])
    test.test_get_order_hole_flop(cards=[0,1,2,3,5,6,7], MAX=8, order=[0,3])
    test.test_get_order_hole_flop(cards=[0,1,2,4,3,5,6], MAX=8, order=[1,0])
    test.test_get_order_hole_flop(cards=[0,1,2,4,3,5,7], MAX=8, order=[1,1])
    test.test_get_order_hole_flop(cards=[0,1,2,4,3,6,7], MAX=8, order=[1,2])
    test.test_get_order_hole_flop(cards=[0,1,2,4,5,6,7], MAX=8, order=[1,3])
