import gambit, os, time

if __name__ == '__main__':

    # directory names
    PARENT_DIRECTORY = ".."
    SAVED_GAMES_DIRECTORY = "saved"
    SOLUTIONS_DIRECTORY = "Solutions-for-PSP-Games-{}".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # file names
    GAME_FILE = "QKA-high-card.gte"

    # read file and create game tree
    os.chdir(SAVED_GAMES_DIRECTORY)
    print("\nStep 1. Begin Reading File...")
    start_time = time.time()
    g = gambit.Game.read_game(GAME_FILE)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done Reading File!\n")

    # get back to the root directory
    os.chdir(PARENT_DIRECTORY)

    # solve the game
    solver = gambit.nash.ExternalEnumMixedSolver()
    print("Step 2. Begin Solving Game...")
    start_time = time.time()
    solutions = solver.solve(g)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done Solving Game!\n")

    # create the solutions directory and cd in
    os.mkdir(SOLUTIONS_DIRECTORY)
    os.chdir(SOLUTIONS_DIRECTORY)
    
    # print the solutions to a file
    print("Step 3. Begin Printing Solutions...")
    start_time = time.time()
    file_name = "{}-PSP.nfg".format(time.strftime("%Y-%m-%d %H:%M:%S"))
    target_file = open(file_name, 'w')
    for solution in solutions:
        target_file.write("{}\n".format(str(solution)))
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done Printing Solutions!\n")

    # get back to the root directory
    os.chdir(PARENT_DIRECTORY)
