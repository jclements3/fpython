"""09_pairs_within_budget -- Count pairs whose sum fits a budget.

Pairs are (i, j) with i < j; values may be negative; the count does
not depend on input order -- that sentence licenses sorting.

Contract:
    pairs_within_budget(t: int, xs: list[int]) -> int

Hint:
    Sort first. Then each element asks: how many LATER elements keep
    the sum <= t? bisect_right(ys, t - x) answers in O(log n) --
    subtract the i+1 elements at or before x itself, clip at 0.

>>> pairs_within_budget(5, [3, 1, 4, 2])
4
>>> pairs_within_budget(-1, [-2, -3, 5])
1
>>> pairs_within_budget(100, [1, 2, 3])
3
>>> pairs_within_budget(0, [1, 2])
0
"""

# -- prelude --
zip_      = lambda a, b: list(zip(a, b))          # shortest wins, any iterable

enum      = lambda xs, start=0: zip_(list(range(start, start + len(xs))), xs)

def bisect_right(a, x):                     # first index where a[i] > x
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"09_pairs_within_budget: {r.attempted - r.failed}/{r.attempted} doctests passing")
