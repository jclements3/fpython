"""03_binary_search -- Index of target in a sorted list, else -1.

Contract:
    binary_search(xs: list, target) -> int

Hint:
    bisect_left finds the leftmost slot where the target COULD be;
    one bounds-check plus one equality test finishes the job. Know
    why bisect_left(xs, x) == len(xs) is possible.

>>> binary_search([1, 3, 5, 7], 5)
2
>>> binary_search([1, 3, 5, 7], 1)
0
>>> binary_search([1, 3, 5, 7], 7)
3
>>> binary_search([1, 3], 2)
-1
>>> binary_search([], 1)
-1
"""

# -- prelude --
def bisect_left(a, x):                      # first index where a[i] >= x
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_binary_search: {r.attempted - r.failed}/{r.attempted} doctests passing")
