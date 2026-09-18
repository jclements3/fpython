"""02_second_largest -- Second largest distinct value.

At least two distinct values guaranteed.

Contract:
    second_largest(xs: list) -> value

Hint:
    nub then sort; the answer is one from the end.

>>> second_largest([1, 5, 3])
3
>>> second_largest([5, 1, 5, 3])
3
>>> second_largest([2, 1])
1
>>> second_largest([-1, -5, -3])
-3
"""

# -- prelude --
nub       = lambda xs: list(dict.fromkeys(xs))    # unique, first occurrence wins (dicts keep order)

# solution goes here
second_largest = lambda xs: sorted(nub(xs))[-2]


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_second_largest: {r.attempted - r.failed}/{r.attempted} doctests passing")
