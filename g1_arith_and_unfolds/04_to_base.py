"""04_to_base -- Render n in base b.

Non-negative n, base 2..16, uppercase digits.

Contract:
    to_base(n: int, b: int) -> str

Hint:
    unfoldr emits digits low-to-high -- "0123456789ABCDEF"[m % b],
    seed m // b, stop at 0. Reverse and join; `or "0"` covers zero
    (its unfold is empty).

>>> to_base(255, 16)
'FF'
>>> to_base(5, 2)
'101'
>>> to_base(0, 8)
'0'
>>> to_base(100, 10)
'100'
>>> to_base(31, 16)
'1F'
"""

# -- prelude --
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
    print(f"04_to_base: {r.attempted - r.failed}/{r.attempted} doctests passing")
