"""03_reverse_digits -- Reverse an integer's digits.

Negatives keep their sign; trailing zeros vanish.

Contract:
    reverse_digits(n: int) -> int

Hint:
    unfoldr peels the digits with (m % 10, m // 10) -- least
    significant first, which IS reversed order. Fold them back into a
    number with acc * 10 + d; signum reapplies the sign.

>>> reverse_digits(123)
321
>>> reverse_digits(-45)
-54
>>> reverse_digits(120)
21
>>> reverse_digits(7)
7
"""

# -- prelude --
signum    = lambda x: (x > 0) - (x < 0)

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

def unfoldr(f, seed):                       # Data.List unfoldr: f(seed) -> None | (value, seed')
    out = []                                # iterate's finite twin: grows a list until f says stop --
    step = f(seed)                          # no more threading (state, acc) tuples through until
    while step is not None:
        val, seed = step
        out.append(val)
        step = f(seed)
    return out

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_reverse_digits: {r.attempted - r.failed}/{r.attempted} doctests passing")
