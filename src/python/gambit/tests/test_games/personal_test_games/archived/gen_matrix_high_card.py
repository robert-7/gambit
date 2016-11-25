import gambit, math, time, os
from fractions import Fraction
from numbers import Rational

def high_card_matrix(num_players, num_cards, title, player_names, ante, bet, mixed=True):
    '''
    Usage: 
    gen.high_card_matrix(num_players=2, num_cards=7, title="PSP Game with 2 Players and 7 Cards", player_names=["Rose","Colin"], ante=1, bet=2)
    '''
    NUM_CHOICES_PER_CARD=2
    num_players=2
    num_strats_per_player=[]
    for i in range(num_players):
        num_strats = math.pow(NUM_CHOICES_PER_CARD, num_cards)
        num_strats_per_player.append(num_strats)
    g = gambit.Game.new_table(num_strats_per_player)
    if title == "":
        g.title = "PSP Game with {} players and {} cards".format(num_players, num_cards)
    else:
        g.title = title
    print("Beginning to compute payoff matrix for {}".format(g.title))

    g.players[0].label = player_names[0]
    g.players[1].label = player_names[1]

    # generate the strategy labels
    form_str="{0:0"+ str(num_cards) +"b}"
    for player in range(len(g.players)):
        for strategy in range(len(g.players[0].strategies)):
            stategy_label = form_str.format(strategy)
            g.players[player].strategies[strategy].label = stategy_label

    # generate the expected payoffs
    for s0 in range(len(g.players[0].strategies)):
        for s1 in range(len(g.players[1].strategies)):
            s0_label = g.players[0].strategies[s0].label
            s1_label = g.players[1].strategies[s1].label
            expected_payoff_rose, expected_payoff_colin = expected_payoffs(s0_label, s1_label, ante, bet, num_cards)
            g[s0,s1][0] = expected_payoff_rose
            g[s0,s1][1] = expected_payoff_colin 

    file_name = "{}-PSP-{}-players-{}-cards.nfg".format(time.strftime("%Y-%m-%d %H:%M:%S"), num_players, num_cards)
    target_file = open(file_name, 'w')
    
    # print the game to target_file
    # print_game(g, target_file)

    # choose the solver needed for this game
    if mixed == True:
        solver = gambit.nash.ExternalEnumMixedSolver()
    else:
        solver = gambit.nash.ExternalEnumPureSolver()

    # start solving the game and record the time it takes to do so
    print("Begin Solving Game...")
    start_time = time.time()
    solutions = solver.solve(g)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done Solving Game!")
    
    # print the solutions to a file
    print("Begin Printing Solutions...")
    for solution in solutions:
        # print(str(solution))
        target_file.write("{}\n".format(str(solution)))
    print("Done Printing Solutions!")

    target_file.close()

def expected_payoffs(s0, s1, ante, bet, num_cards):
    total_payoff_rose = 0
    total_payoff_colin = 0

    for i in range(num_cards):
        for j in range(num_cards):

            if i == j:
                continue

            payoff_rose, payoff_colin = calculate_payoffs(s0, s1, i, j, ante, bet)

            # print ("s0={}\ts1={}\ti={}\tj={}\tpayoff_rose={}\tpayoff_colin={}".format(s0, s1, i, j, payoff_rose, payoff_colin))

            total_payoff_rose += payoff_rose
            total_payoff_colin += payoff_colin


    total_possilities = num_cards**2 - num_cards
    expected_payoff_rose = Fraction(total_payoff_rose, total_possilities)
    expected_payoff_colin = Fraction(total_payoff_colin, total_possilities)

    # print("expected_payoff_rose={}  \ts0={}  \texpected_payoff_colin={}  \ts1={}".format(expected_payoff_rose, s0, expected_payoff_colin, s1))
    return expected_payoff_rose, expected_payoff_colin

def calculate_payoffs(s0, s1, i, j, ante, bet):
    pot = 0
    payoff_rose = 0
    payoff_rose -= ante
    pot += ante
    payoff_colin = 0
    payoff_colin -= ante
    pot += ante

    if checks(s0,i):
        if i > j:
            payoff_rose += pot
        else:
            payoff_colin += pot

    elif bets(s0,i):
        payoff_rose -= bet
        pot += bet

        if folds(s1,j):
            payoff_rose += pot

        elif calls(s1,j):
            payoff_colin -= bet
            pot += bet
            if (i > j):
                payoff_rose += pot
            else:
                payoff_colin += pot

    # print("payoff_rose={}\ts0={}\tpayoff_colin={}\ts1={}\ti={}\tj={}".format(payoff_rose, s0, payoff_colin, s1, i, j))
    return payoff_rose, payoff_colin

def checks(s, n):
    choice = s[-1-n]
    return choice == '0'

def bets(s, n):
    choice = s[-1-n]
    return choice == '1'

def folds(s, n):
    choice = s[-1-n]
    return choice == '0'

def calls(s, n):
    choice = s[-1-n]
    return choice == '1'

def print_game(g, target_file):
    print("Start Printing Game...")
    serialized = g.write()
    target_file.write(serialized)
    print("Done Printing Game!")

if __name__ == '__main__':
    folder = "Solutions-for-PSP-Games-{}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    os.mkdir(folder)
    os.chdir(folder)
    for n in range(2, 5):
        high_card_matrix(num_players=2, num_cards=n, title="", player_names=["Rose","Colin"], ante=1, bet=2, mixed=True)
