from deuces.evaluator import Evaluator 
from deuces.lookup import LookupTable
from deuces.card import Card


def return_winner(g):

    # create hands and board    
    hand1 = [
        Card.new(g.cards_in_play[0]),
        Card.new(g.cards_in_play[1])
    ]
    hand2 = [
        Card.new(g.cards_in_play[2]),
        Card.new(g.cards_in_play[3])
    ]
    board = [
        Card.new(g.cards_in_play[4]),
        Card.new(g.cards_in_play[5]),
        Card.new(g.cards_in_play[6]),
        Card.new(g.cards_in_play[7]),
        Card.new(g.cards_in_play[8])
    ]

    # evaluate the hands
    evaluator   = Evaluator()
    hand1_rank  = evaluator.evaluate(board, hand1)
    hand1_class = evaluator.get_rank_class(hand1_rank)
    hand1_class_str = evaluator.class_to_string(hand1_class)
    hand2_rank  = evaluator.evaluate(board, hand2)
    hand2_class = evaluator.get_rank_class(hand2_rank)
    hand2_class_str = evaluator.class_to_string(hand2_class)

    # for testing purposes
    if g.DEBUG:
        print("hand1_rank={}, hand1_class_str={}, hand2_rank={}, hand2_class_str={}".format(
               hand1_rank,    hand1_class_str,    hand2_rank,    hand2_class_str))

    # we need to adjust the rank if our lowest card is a 6 or 7
    if g.LOWEST_CARD == 6 or g.LOWEST_CARD == 7:
        hand1_rank = adjust_rank(hand1_rank, hand1_class)
        hand2_rank = adjust_rank(hand2_rank, hand2_class)

    # return the winner
    if hand1_rank < hand2_rank:
        return g.tree.players[0]
    elif hand1_rank > hand2_rank:
        return g.tree.players[1]
    else:
        return None


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
