import os
import pudb; pu.db

output_folder = "output"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)
os.chdir(output_folder)

output_folders = os.listdir(".")
output_folders.sort()
last_output_folder = output_folders[-1]

if not os.path.exists(last_output_folder):
    os.mkdir(last_output_folder)
os.chdir(last_output_folder)

infile = "Game-Tree"
outfile = "Game-Tree-Truncated"

if os.path.exists(outfile):
    os.remove(outfile)

f = file(infile, 'r')
g = file(outfile, 'w')

expected_value_for_betting  = 0.0
expected_value_for_checking = 0.0

total_branches = 0

lines = f.readlines()

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

for line in lines:
    if line.startswith('t'):
        line = line[44:].strip()
        skipped_line = line[3:]

        if skipped_line.startswith("XB0-YR0-XK0") or skipped_line.startswith("XB0-YR0-XF1"):
            probability = 1.0/12
        elif skipped_line.startswith("XB0-YK1") or skipped_line.startswith("XB0-YF2"):
            probability = 1.0/6
        elif skipped_line.startswith("XC1-YB0-XK0") or skipped_line.startswith("XC1-YB0-XF1"):
            probability = 1.0/8
        elif skipped_line.startswith("XC1-YC1"):
            probability = 1.0/4
        else:
            raise Exception("bad line {}".format(skipped_line))
        
        outcome = int(line.split('{')[1].split(',')[0].strip())
        expected_value = outcome*probability

        if skipped_line.startswith("XB"):
            expected_value_for_betting += expected_value
            bet_or_check = "BET"
        elif skipped_line.startswith("XC"):
            expected_value_for_checking += expected_value
            bet_or_check = "CHECK"
        else:
            raise Exception("bad line {}".format(skipped_line))

        new_line = "{} - {} - {} - {}\n".format(line.strip(), bet_or_check, str(probability), str(expected_value))

        g.write(new_line)

new_line = "expected_value_for_betting ({}) - expected_value_for_checking ({})\n".format(str(expected_value_for_betting/total_branches), str(expected_value_for_checking/total_branches))
g.write(new_line)

f.close()
g.close()


PARENT_DIRECTORY = ".."

# go back out
os.chdir(PARENT_DIRECTORY)
os.chdir(PARENT_DIRECTORY)
