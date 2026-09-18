"""07_lis -- Longest strictly increasing subsequence (length).

Contract:
    lis(xs: list[int]) -> int

Hint:
    Patience sorting: fold the sequence into `tails`, where tails[i]
    is the smallest possible tail of an increasing run of length i+1.
    bisect_left says which pile each element lands on; a landing past
    the end grows the answer. O(n log n) where the obvious DP is
    O(n^2) -- say both.

>>> lis([10, 9, 2, 5, 3, 7, 101, 18])
4
>>> lis([5, 4, 3])
1
>>> lis([1, 2, 3])
3
>>> lis([])
0
>>> lis([7, 7, 7])
1
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

NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

def foldl(f, xs, base=NOTHING):           # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if base is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = base
    for x in it:
        acc = f(acc, x)
    return acc

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"07_lis: {r.attempted - r.failed}/{r.attempted} doctests passing")
