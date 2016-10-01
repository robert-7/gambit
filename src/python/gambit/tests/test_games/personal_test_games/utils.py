import time

'''
We compute the duration of time for which the function ran.
'''
def compute_time_of(step_number, step_action, function, args):
    print("\nStep {}: {}...".format(step_number, step_action))
    start_time = time.time()
    return_value = function(*args)
    print("--- %s seconds ---" % (time.time() - start_time))
    print("Done {}!\n".format(step_action))
    return return_value
