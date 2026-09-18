"""09_totals_and_deltas -- A scan and its inverse.

Contract:
    running_totals(xs: list) -> list   # cumulative sums
    deltas(xs: list) -> list           # each element minus the previous

Hint:
    running_totals IS scanl1 (+). deltas is the pairwise differences.
    They undo each other: prepend the first element to
    deltas(running_totals(xs)) and xs comes back -- say why.

>>> running_totals([3, 1, 4])
[3, 4, 8]
>>> running_totals([])
[]
>>> deltas([5, 3, 8])
[-2, 5]
>>> deltas([7])
[]
>>> ts = running_totals([2, 5, 1]); [2] + deltas(ts) == [2, 5, 1]
True
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

scanl1 = lambda f, xs: list(accumulate(xs, f))

pairwise  = lambda xs: list(zip(xs, xs[1:]))              # zip xs (tail xs)

map_      = lambda f, xs: [f(x) for x in xs]

# solution goes here
running_totals = lambda xs: scanl1(add, xs)
deltas = lambda xs: map_(lambda p: p[1] - p[0], pairwise(xs))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"09_totals_and_deltas: {r.attempted - r.failed}/{r.attempted} doctests passing")
