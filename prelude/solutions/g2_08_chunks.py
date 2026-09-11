"""08_chunks -- Split a list into pieces of length k.

Last piece may be shorter.

Contract:
    chunks(xs: list, k: int) -> list[list]

Hint:
    splitAt already returns (front, rest) == (value, next_seed), so
    chunks IS unfoldr of splitAt; null(rest) is the stop. One line.
    (You are deriving the prelude's chunksOf -- deriving a tool once
    is why it sticks.)

>>> chunks([1, 2, 3, 4, 5], 2)
[[1, 2], [3, 4], [5]]
>>> chunks([1, 2, 3, 4], 2)
[[1, 2], [3, 4]]
>>> chunks([], 3)
[]
>>> chunks([1], 5)
[[1]]
"""

# -- prelude --
null      = lambda xs: len(xs) == 0

splitAt   = lambda n, xs: (xs[:n], xs[n:]) if n >= 0 else (xs[:0], xs)   # n<0 splits at the front

def unfoldr(f, seed):                       # Data.List unfoldr: f(seed) -> None | (value, seed')
    out = []                                # iterate's finite twin: grows a list until f says stop --
    step = f(seed)                          # no more threading (state, acc) tuples through until
    while step is not None:
        val, seed = step
        out.append(val)
        step = f(seed)
    return out

# solution goes here
chunks = lambda xs, k: unfoldr(
    lambda rest: None if null(rest) else splitAt(k, rest), list(xs))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"08_chunks: {r.attempted - r.failed}/{r.attempted} doctests passing")
