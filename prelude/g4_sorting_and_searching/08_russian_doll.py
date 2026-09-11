"""08_russian_doll -- LC 354: Russian Doll Envelopes.

Envelope (w, h) fits inside another only when BOTH are strictly
smaller. No rotation. Longest nesting chain.

Contract:
    max_dolls(envelopes: list[tuple[int, int]]) -> int

Hint:
    Sort by (width asc, height DESC), then plain LIS on the heights
    -- g4_07 verbatim. The descending tie-break is the whole trick:
    equal-width envelopes arrive tallest-first, so no two of them can
    ever chain in a strictly-increasing height run. Sorting
    linearized one dimension; LIS handles the other. O(n log n).

>>> max_dolls([(5, 4), (6, 4), (6, 7), (2, 3)])
3
>>> max_dolls([(1, 1), (1, 1), (1, 1)])
1
>>> max_dolls([(3, 4), (3, 5), (3, 6)])
1
>>> max_dolls([])
0
>>> max_dolls([(2, 3)])
1
"""

# -- prelude --
sortOn = lambda f, xs: sorted(xs, key=f)    # sortOn (schwartzian, f called once per element)

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

def foldl(f, xs, init=NOTHING):           # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if init is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = init
    for x in it:
        acc = f(acc, x)
    return acc

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"08_russian_doll: {r.attempted - r.failed}/{r.attempted} doctests passing")
