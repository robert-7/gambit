import os
import pudb; pu.db

player = 1
output_folder = "output"

# cd into output folder
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
os.chdir(output_folder)

# cd into last output directory
output_folders = os.listdir(".")
output_folders.sort()
last_output_folder = output_folders[-1]

if not os.path.exists(last_output_folder):
    os.mkdir(last_output_folder)
os.chdir(last_output_folder)

infile = "Game-Tree"
outfile = "Game-Tree-Truncated"

# remove file if it currently exists
if os.path.exists(outfile):
    os.remove(outfile)

# create file descriptors
f = file(infile, 'r')
g = file(outfile, 'w')

# the expected values
expected_value_for_betting  = 0.0
expected_value_for_checking = 0.0

# the total number of branches
total_branches = 0

# read the lines
lines = f.readlines()

# get number of branches
for line in lines:
    if line.startswith('c'):
        
        # ends with "1/6 } 0"
        last_right_curly_index = line.rfind('}')
        line = line[:last_right_curly_index]
        last_slash_index = line.rfind('/')
        line = line[last_slash_index+1:]
        line = line.strip()
        total_branches = int(line)
        break

# for each line
for line in lines:
    if line.startswith('t'):
        
        # ignore first few lines with no information
        line = line[44:].strip()
        skipped_line = line[3:]
        
        # get the outcomes
        outcomes = line.split('{')[1].split('}')[0].split(',')

        # if we're focusing on player 1...
        if player == 1:

            # get the corrent outcome
            outcome = int(outcomes[0].strip())

            # set the probabilities 
            if skipped_line.startswith("XB0-YR0-XK0") or skipped_line.startswith("XB0-YR0-XF1"):
                probability = 1.0/12
            elif skipped_line.startswith("XB0-YK1") or skipped_line.startswith("XB0-YF2"):
                probability = 1.0/6
            elif skipped_line.startswith("XC1-YB0-XK0") or skipped_line.startswith("XC1-YB0-XF1"):
                probability = 1.0/8
            elif skipped_line.startswith("XC1-YC1"):
                probability = 1.0/4
            else:
                error_msg = "Bad line {}. Perhaps your player number is incorrect."
                raise Exception(error_msg.format(skipped_line))

        # otherwise...
        else:

            # get the corrent outcome
            outcome = int(outcomes[1].strip())

            # set the probabilities
            if skipped_line.startswith("XC1-YB0-XK0") or skipped_line.startswith("XC1-YB0-XF1"):
                probability = 1.0/4
            elif skipped_line.startswith("XC1-YC1"):
                probability = 1.0/2
            else:
                error_msg = "Bad line {}. Perhaps your player number is incorrect."
                raise Exception(error_msg.format(skipped_line))

        # get the expected value of making that choice
        expected_value = outcome*probability

        # if we're focusing on player 1...
        if player == 1:

            # add the expected value to the correct sum
            if skipped_line.startswith("XB"):
                expected_value_for_betting += expected_value
                bet_or_check = "BET"
            elif skipped_line.startswith("XC"):
                expected_value_for_checking += expected_value
                bet_or_check = "CHECK"
            else:
                raise Exception("bad line {}".format(skipped_line))

        # otherwise...
        else:

            # add the expected value to the correct sum
            if skipped_line.startswith("XC1-YB"):
                expected_value_for_betting += expected_value
                bet_or_check = "BET"
            elif skipped_line.startswith("XC1-YC"):
                expected_value_for_checking += expected_value
                bet_or_check = "CHECK"
            else:
                raise Exception("bad line {}".format(skipped_line))

        # write the new output line
        new_line = "{} - {} - {} - {}\n".format(line.strip(), bet_or_check, str(probability), str(expected_value))
        g.write(new_line)

# add the conclusion line
new_line = "expected_value_for_betting ({}) - expected_value_for_checking ({})\n".format(str(expected_value_for_betting/total_branches), str(expected_value_for_checking/total_branches))
g.write(new_line)

# close the file descriptor
f.close()
g.close()


# go back out
PARENT_DIRECTORY = ".."
os.chdir(PARENT_DIRECTORY)
os.chdir(PARENT_DIRECTORY)
