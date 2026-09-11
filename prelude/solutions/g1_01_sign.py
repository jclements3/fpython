"""01_sign -- Sign of a number.

Return -1 for negative, 0 for zero, 1 for positive.

Contract:
    sign(x: int | float) -> int

Hint:
    The prelude ships this exact function: signum, one comparison
    subtraction, no branches. Recognize it, don't reinvent it.

>>> sign(-7)
-1
>>> sign(0)
0
>>> sign(3)
1
>>> sign(-0.5)
-1
"""

# -- prelude --
signum    = lambda x: (x > 0) - (x < 0)

# solution goes here
sign = signum


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_sign: {r.attempted - r.failed}/{r.attempted} doctests passing")
