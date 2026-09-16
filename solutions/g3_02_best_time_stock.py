"""02_best_time_stock -- NeetCode: Best Time to Buy and Sell Stock.

Contract:
    max_profit(prices: list[int]) -> int
    One buy, one later sell. Best achievable profit, 0 if none.
    len(prices) >= 1.

Hint:
    scanl1 min gives the running minimum -- the best buy so far.
    zipWith (-) prices against it, then maximum. A scan, not a loop.

>>> max_profit([7, 1, 5, 3, 6, 4])
5
>>> max_profit([7, 6, 4, 3, 1])
0
>>> max_profit([5])
0
"""

# -- prelude --
NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

add       = lambda a, b: a + b                                           # (+) as a value: scanl1(add, xs)
sub       = lambda a, b: a - b                                           # (-) as a value: zipWith(sub, a, b)

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

zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]

# solution goes here
def max_profit(prices):
    mins = scanl1(min, prices)
    return max(zipWith(sub, prices, mins))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_best_time_stock: {r.attempted - r.failed}/{r.attempted} doctests passing")
