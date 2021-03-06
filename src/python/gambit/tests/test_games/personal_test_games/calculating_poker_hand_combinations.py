import itertools 
from deuces.evaluator import Evaluator 
from deuces.lookup import LookupTable
import math_extended


class General_Poker_LookupTable(object):
    """
    Here we create a lookup table which maps:
        5 card hand's unique prime product => rank in range [1, 7462]
    Examples:

    Number of Distinct Hand Values for Standard Poker Game with 13 Values:
    Straight Flush   10          [(10 choose 1)]
    Four of a Kind   156         [(13 choose 2) * (2 choose 1)]
    Full Houses      156         [(13 choose 2) * (2 choose 1)]
    Flush            1277        [(13 choose 5) - 10 straight flushes]
    Straight         10          [(10 choose 1)]
    Three of a Kind  858         [(13 choose 3) * (3 choose 1)]
    Two Pair         858         [(13 choose 3) * (3 choose 2)]
    One Pair         2860        [(13 choose 4) * (4 choose 1)]
    High Card      + 1277        [(13 choose 5) - 10 straights]
    -------------------------
    TOTAL            7462
    
    If the Ace DOES NOT Wrap around, then there are still 7462 Distinct Hand Values. Reasoning:
    -- 1 Less Straight Flush
    ---- And therefore, 1 More Flush
    -- 1 Less Straight
    ---- And therefore, 1 More High Card

    * Royal flush (best hand possible)          => 1
    * 7-5-4-3-2 unsuited (worst hand possible)  => 7462

    Number of Distinct Hand Values for Standard Poker Game with 1 < n < 13 Values:
    Straight Flush   n-4         [((n-4) choose 1)]
    Four of a Kind   2*n_C_2     [(n choose 2) * (2 choose 1)]
    Full Houses      2*n_C_2     [(n choose 2) * (2 choose 1)]
    Flush            n_C_5 - n-4 [(n choose 5) - n-4 straight flushes]
    Straight         n-4         [((n-4) choose 1)]
    Three of a Kind  3*n_C_3     [(n choose 3) * (3 choose 1)]
    Two Pair         3*n_C_3     [(n choose 3) * (3 choose 2)]
    One Pair         4*n_C_4     [(n choose 4) * (4 choose 1)]
    High Card      + n_C_5 - n-4 [(n choose 5) - n-4 straights]
    -------------------------
    TOTAL            ??? (something ugly)
    """


    def __init__(self):
        self.STRAIGHT_FLUSH  = 1
        self.FOUR_OF_A_KIND  = 2
        self.FULL_HOUSE      = 3
        self.FLUSH           = 4         
        self.STRAIGHT        = 5
        self.THREE_OF_A_KIND = 6
        self.TWO_PAIR        = 7
        self.ONE_PAIR        = 8
        self.HIGH_CARD       = 9


def get_total_distinct_number(n, s):
    # holds the total sum
    total = 0

    # iterating over all possible hands...
    for r in range(1,10):
        total += get_distinct_number(r, n, s)
    return total


def get_distinct_number(hand_rank, n, s):
    # holds the number of distinct combinations
    dc = 0

    if hand_rank == r.STRAIGHT_FLUSH:
        if n < 5:
            dc = 0
        else:
            dc = math_extended.combinations(n-4,1)
    elif hand_rank == r.FOUR_OF_A_KIND:
        if n < 2 or s < 4:
            dc = 0
        else:
            dc = math_extended.combinations(n,2) * math_extended.combinations(2,1)
    elif hand_rank == r.FULL_HOUSE:
        if n < 2 or s < 3:
            dc = 0
        else:
            dc = math_extended.combinations(n,2) * math_extended.combinations(2,1)
    elif hand_rank == r.FLUSH:
        if n < 5 or s < 2:
            dc = 0
        else:
            dc = math_extended.combinations(n,5) - get_distinct_number(r.STRAIGHT_FLUSH, n, s)
    elif hand_rank == r.STRAIGHT:
        if n < 5:
            dc = 0
        else:
            dc = math_extended.combinations(n-4,1)
    elif hand_rank == r.THREE_OF_A_KIND:
        if n < 3 or s < 3:
            dc = 0
        else:
            dc = math_extended.combinations(n,3) * math_extended.combinations(3,1)
    elif hand_rank == r.TWO_PAIR:
        if n < 3 or s < 2:
            dc = 0
        else:
            dc = math_extended.combinations(n,3) * math_extended.combinations(3,1)
    elif hand_rank == r.ONE_PAIR:
        if n < 4 or s < 2:
            dc = 0
        else:
            dc = math_extended.combinations(n,4) * math_extended.combinations(4,1)
    elif hand_rank == r.HIGH_CARD:
        if n < 5:
            dc = 0
        else:
            dc = math_extended.combinations(n,5) - get_distinct_number(r.STRAIGHT_FLUSH, n, s)
    else:
        raise Exception("{} is not a possible string for hand_rank".format(hand_rank))

    # we want to output the number of distinct hands for each class
    class_str = LookupTable.RANK_CLASS_TO_STRING[hand_rank]
    class_count = "The number of different ways to obtain a {} with {} cards is: {}"
    print(class_count.format(class_str.ljust(15), str(n).ljust(2), dc))

    return dc


if __name__ == "__main__":
    
    # number of suits 
    s = 4

    # create the lookup table
    r = General_Poker_LookupTable()

    # for each number of values, we want to print out
    for n in range(1, 14):
        
        # the total distinct number of hands
        td = get_total_distinct_number(n, s)

        # the format we'd like to print in
        pf = "Number of distinct ranks for {} number of cards: {}"
        
        print(pf.format(n, td))
        print()
