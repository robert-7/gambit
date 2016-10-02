from deuces.evaluator import Evaluator 
from deuces.lookup import LookupTable


def return_winner(board, player_1_hand, player_2_hand, n):
    
    # evaluate the hands
    evaluator   = Evaluator()
    card_rank1  = evaluator.evaluate(board, player_1_hand)
    class_rank1 = evaluator.get_rank_class(rank1)
    card_rank2  = evaluator.evaluate(board, player_2_hand)
    class_rank2 = evaluator.get_rank_class(rank2)

    # we need to adjust the rank if our lowest card is a 6 or 7
    if n == 6 or n == 7:
        rank1 = adjust_rank(card_rank1, class_rank1)
        rank2 = adjust_rank(card_rank2, class_rank2)

    # return the winner
    if rank1 < rank2:
        return rank1
    elif rank1 > rank2:
        return rank2
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
