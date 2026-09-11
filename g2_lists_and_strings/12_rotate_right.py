"""12_rotate_right -- Rotate a list right by k.

k may be 0 or larger than the list.

Contract:
    rotate_right(xs: list, k: int) -> list

Hint:
    One splitAt at len - k%len, then glue the halves swapped.
    The k=0 trap: xs[-0:] thinking sneaks in if you slice by -k.

>>> rotate_right([1, 2, 3, 4, 5], 2)
[4, 5, 1, 2, 3]
>>> rotate_right([1, 2], 0)
[1, 2]
>>> rotate_right([1, 2, 3], 5)
[2, 3, 1]
>>> rotate_right([], 3)
[]
"""

# -- prelude --
splitAt   = lambda n, xs: (xs[:n], xs[n:]) if n >= 0 else (xs[:0], xs)   # n<0 splits at the front

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"12_rotate_right: {r.attempted - r.failed}/{r.attempted} doctests passing")
