from deuces.evaluator import Evaluator 
from deuces.lookup import LookupTable
from deuces.card import Card
from sys import stdout

class Manila_Poker_Mapping(object):

    def __init__(self):
        self.alsm = self.create_alsm()

    def create_alsm(self):

        # the table containing all ranks where the Ace could be in a straight, depending on the lowest card
        # we'll call it, ace-low-straight-map
        # this will be the mapping:
        # A3456 -> 23456
        # A4567 -> 34567
        # A5678 -> 45678
        # A6789 -> 56789
        # A789T -> 6789T
        # A89TJ -> 789TJ
        # A9TJQ -> 89TJQ
        # However, we should obtain the rank of the hands through calculation, 
        # rather than store their values
        evaluator = Evaluator()
        offsuit_A3456_rank = evaluator.evaluate(create_cards(["Ah","3h","4h","5h","6h"]),[])
        offsuit_A4567_rank = evaluator.evaluate(create_cards(["Ah","4h","5h","6h","7h"]),[])
        offsuit_A5678_rank = evaluator.evaluate(create_cards(["Ah","5h","6h","7h","8h"]),[])
        offsuit_A6789_rank = evaluator.evaluate(create_cards(["Ah","6h","7h","8h","9h"]),[])
        offsuit_A789T_rank = evaluator.evaluate(create_cards(["Ah","7h","8h","9h","Th"]),[])
        offsuit_A89TJ_rank = evaluator.evaluate(create_cards(["Ah","8h","9h","Th","Jh"]),[])
        offsuit_A9TJQ_rank = evaluator.evaluate(create_cards(["Ah","9h","Th","Jh","Qh"]),[])

        offsuit_23456_rank = evaluator.evaluate(create_cards(["2h","3h","4h","5h","6h"]),[])
        offsuit_34567_rank = evaluator.evaluate(create_cards(["3h","4h","5h","6h","7h"]),[])
        offsuit_45678_rank = evaluator.evaluate(create_cards(["4h","5h","6h","7h","8h"]),[])
        offsuit_56789_rank = evaluator.evaluate(create_cards(["5h","6h","7h","8h","9h"]),[])
        offsuit_6789T_rank = evaluator.evaluate(create_cards(["6h","7h","8h","9h","Th"]),[])
        offsuit_789TJ_rank = evaluator.evaluate(create_cards(["7h","8h","9h","Th","Jh"]),[])
        offsuit_89TJQ_rank = evaluator.evaluate(create_cards(["8h","9h","Th","Jh","Qh"]),[])

        onsuit_A3456_rank  = evaluator.evaluate(create_cards(["Ah","3h","4h","5h","6c"]),[])
        onsuit_A4567_rank  = evaluator.evaluate(create_cards(["Ah","4h","5h","6h","7c"]),[])
        onsuit_A5678_rank  = evaluator.evaluate(create_cards(["Ah","5h","6h","7h","8c"]),[])
        onsuit_A6789_rank  = evaluator.evaluate(create_cards(["Ah","6h","7h","8h","9c"]),[])
        onsuit_A789T_rank  = evaluator.evaluate(create_cards(["Ah","7h","8h","9h","Tc"]),[])
        onsuit_A89TJ_rank  = evaluator.evaluate(create_cards(["Ah","8h","9h","Th","Jc"]),[])
        onsuit_A9TJQ_rank  = evaluator.evaluate(create_cards(["Ah","9h","Th","Jh","Qc"]),[])
        
        onsuit_23456_rank  = evaluator.evaluate(create_cards(["2h","3h","4h","5h","6c"]),[])
        onsuit_34567_rank  = evaluator.evaluate(create_cards(["3h","4h","5h","6h","7c"]),[])
        onsuit_45678_rank  = evaluator.evaluate(create_cards(["4h","5h","6h","7h","8c"]),[])
        onsuit_56789_rank  = evaluator.evaluate(create_cards(["5h","6h","7h","8h","9c"]),[])
        onsuit_6789T_rank  = evaluator.evaluate(create_cards(["6h","7h","8h","9h","Tc"]),[])
        onsuit_789TJ_rank  = evaluator.evaluate(create_cards(["7h","8h","9h","Th","Jc"]),[])
        onsuit_89TJQ_rank  = evaluator.evaluate(create_cards(["8h","9h","Th","Jh","Qc"]),[])

        # the dictionary defining the necessary mappings, # ace-low-straight-map
        alsm = {
                    (offsuit_A3456_rank,3) : offsuit_23456_rank,
                    (offsuit_A4567_rank,4) : offsuit_34567_rank,
                    (offsuit_A5678_rank,5) : offsuit_45678_rank,
                    (offsuit_A6789_rank,6) : offsuit_56789_rank,
                    (offsuit_A789T_rank,7) : offsuit_6789T_rank,
                    (offsuit_A89TJ_rank,8) : offsuit_789TJ_rank,
                    (offsuit_A9TJQ_rank,9) : offsuit_89TJQ_rank,

                    (onsuit_A3456_rank,3)  : onsuit_23456_rank,
                    (onsuit_A4567_rank,4)  : onsuit_34567_rank,
                    (onsuit_A5678_rank,5)  : onsuit_45678_rank,
                    (onsuit_A6789_rank,6)  : onsuit_56789_rank,
                    (onsuit_A789T_rank,7)  : onsuit_6789T_rank,
                    (onsuit_A89TJ_rank,8)  : onsuit_789TJ_rank,
                    (onsuit_A9TJQ_rank,9)  : onsuit_89TJQ_rank
               }
        return alsm

    
class Manila_Poker_Evaluator(Evaluator):
    def __init__(self):
        super(Manila_Poker_Evaluator, self).__init__()


    def evaluate(self, g, hand, board):
        
        # obtain the rank through the superclass method
        hand_rank = super(Manila_Poker_Evaluator, self).evaluate(hand, board)

        # we should adjust the rank
        if g.ACE_WRAPS and (2 < g.LOWEST_CARD < 10):
            hand_rank = adjust_rank_if_ace_wrap(hand_rank, g.LOWEST_CARD, g.mpm)

        # get the class of each hand
        hand_class     = super(Manila_Poker_Evaluator, self).get_rank_class(hand_rank)
        hand_class_str = super(Manila_Poker_Evaluator, self).class_to_string(hand_class)

        # we need to adjust the rank if our lowest card is a 6 or 7
        if g.LOWEST_CARD == 6 or g.LOWEST_CARD == 7:
            hand_rank = adjust_rank(hand_rank, hand_class)

        # for testing purposes
        if g.DEBUG:
            print("hand_rank={}, hand_class_str={}".format(hand_rank, hand_class_str))

        return hand_rank


def return_winner(g):

    # create hands and board
    hand1, hand2, board = create_hands_and_board(g)

    # evaluate the hands
    mpe         = Manila_Poker_Evaluator()
    hand1_rank  = mpe.evaluate(g, hand1, board)
    hand2_rank  = mpe.evaluate(g, hand2, board)

    # return the winner
    if hand1_rank < hand2_rank:
        return g.tree.players[0]
    elif hand1_rank > hand2_rank:
        return g.tree.players[1]
    else:
        return None

def create_hands_and_board(g):

    # verify our cards are valid
    # most checks are done, so we just need to create a card
    # only if it's value is higher than or equal to the value of the
    # lowest card allowed

    for card in g.cards_in_play:

        # get value of card as a string, or card_value = cv and card_value_string = cvs
        cvs = card[0]
        if cvs != "T" and cvs != "J" and cvs != "Q" and cvs != "K" and cvs != "A":
            try:
                cv = int(cvs)
            except Exception:
                error_msg = "You did not put a valid number of letter for the value of card {}"
                raise ValueError(error_msg.format(card))

            # if cv is less than the allowed value, than we should stop the execution
            if cv < g.LOWEST_CARD:
                error_msg = '''You must supply a card with value greater than or equal to {}. 
                The value {} was given.'''
                raise ValueError(error_msg.format(g.LOWEST_CARD, cv))

    # create the hands and board
    hand1 = create_cards(g.cards_in_play[0:2])
    hand2 = create_cards(g.cards_in_play[2:4])
    board = create_cards(g.cards_in_play[4:])
    
    if g.DEBUG:
        stdout.write("hand1=")
        Card.print_pretty_cards(hand1)
        stdout.write("hand2=")
        Card.print_pretty_cards(hand2)
        stdout.write("board=")
        Card.print_pretty_cards(board)

    return hand1, hand2, board

def create_cards(cards):

    # we want to return a list of Card objects, given the string label
    ret_cards = []
    for card in cards:
        ret_cards.append(Card.new(card))

    return ret_cards

def adjust_rank_if_ace_wrap(card_rank, n, mpm):

    # if our card's rank is in the dictionary 
    # AND it's lowest non-Ace card number is our lowest number in this game...
    if (card_rank,n) in mpm.alsm:
        card_rank = mpm.alsm[(card_rank,n)]

    return card_rank


def adjust_rank(card_rank, class_rank):

    # if we have a full house, we need to decrease our rank by the number of flush possibilities
    if class_rank == LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FULL_HOUSE]:        
        card_rank += LookupTable.MAX_FLUSH - LookupTable.MAX_FULL_HOUSE

    # if we have a flush, we need to increase our rank by the number of full house possibilities
    elif class_rank == LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_FLUSH]:        
        card_rank -= LookupTable.MAX_FULL_HOUSE - LookupTable.MAX_FOUR_OF_A_KIND

    # if we have a straight, we need to decrease our rank by the number of three of a kind possibilities
    elif class_rank == LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_STRAIGHT]:   
        card_rank += LookupTable.MAX_THREE_OF_A_KIND - LookupTable.MAX_STRAIGHT

    # if we have a three of a kind, we need to increase our rank by the number of full house possibilities
    elif class_rank == LookupTable.MAX_TO_RANK_CLASS[LookupTable.MAX_THREE_OF_A_KIND]: 
        card_rank -= LookupTable.MAX_STRAIGHT - LookupTable.MAX_FLUSH

    return card_rank
