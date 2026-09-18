"""05_moving_average -- Average of every k-window.

Contract:
    moving_average(xs: list, k: int) -> list[float]
    len(xs) >= k >= 1.

Hint:
    Prefix sums = scanl (+) 0 -- one scan, then every window sum is
    pref[i+k] - pref[i]: zipWith (-) the two offset views of the same
    scan, divide by k.

>>> moving_average([1, 2, 3, 4], 2)
[1.5, 2.5, 3.5]
>>> moving_average([1, 1, 1], 3)
[1.0]
>>> moving_average([5], 1)
[5.0]
"""

# -- prelude --
NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

add       = lambda a, b: a + b                                           # (+) as a value: scanl1(add, xs)

def accumulate(xs, f=None, initial=NOTHING):     # scanl / scanl1
    if f is None:
        f = add
    it = iter(xs)
    if initial is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            return
    else:
        acc = initial
    yield acc
    for x in it:
        acc = f(acc, x)
        yield acc

scanl  = lambda f, z, xs: list(accumulate(xs, f, initial=z))

zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_moving_average: {r.attempted - r.failed}/{r.attempted} doctests passing")
