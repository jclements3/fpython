"""06_from_roman -- Parse a valid Roman numeral.

Contract:
    from_roman(s: str) -> int

Hint:
    pairwise gives each symbol its right neighbor; a value counts
    NEGATIVE when its neighbor is bigger ('IV' = -1 + 5). Pad the
    value list with a trailing 0 so the last symbol gets a neighbor
    too, then sum.

>>> from_roman('MCMXCIV')
1994
>>> from_roman('IX')
9
>>> from_roman('LVIII')
58
>>> from_roman('III')
3
>>> from_roman('MMM')
3000
"""

# -- prelude --
map_      = lambda f, xs: [f(x) for x in xs]

pairwise  = lambda xs: list(zip(xs, xs[1:]))              # zip xs (tail xs)

# solution goes here
VAL = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}

def from_roman(s):
    vs = map_(lambda c: VAL[c], s) + [0]
    return sum(map_(lambda p: -p[0] if p[0] < p[1] else p[0], pairwise(vs)))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"06_from_roman: {r.attempted - r.failed}/{r.attempted} doctests passing")
