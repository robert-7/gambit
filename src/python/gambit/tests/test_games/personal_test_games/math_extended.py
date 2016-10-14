from math import factorial

def combinations(n,k):
    if (n < k) or (k < 0):
	    raise ValueError("Either n < k or k < 0: n = {}, k = {}.".format(n, k))
    numerator=factorial(n)
    denominator=(factorial(k)*factorial(n-k))
    answer=numerator/denominator
    return answer

def sum_first_n_values(n):

    # error handler
    if n < 0 or type(n) is not int:
        error_msg = "Can't take the sum of the the first 'n' values for n={}"
        raise Exception(error_msg.format(n))
    
    # known formula for computing the sum of the first n values
    s = ((n)*(n+1))/2
    return s
