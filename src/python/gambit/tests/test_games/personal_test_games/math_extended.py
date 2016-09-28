from math import factorial

def combinations(n,k):
    if (n < k) or (k < 0):
	    raise ValueError("Either n < k or k < 0: n = {}, k = {}.".format(n, k))
    numerator=factorial(n)
    denominator=(factorial(k)*factorial(n-k))
    answer=numerator/denominator
    return answer