"""01_coin_change -- NeetCode: Coin Change.

Contract:
    coin_change(coins: list[int], amount: int) -> int
    Fewest coins summing to amount (unlimited supply), -1 if impossible.
    amount >= 0, coins positive.

Hint:
    Knapsack, dp[remaining]. Top-down with memo on the single
    index `amount` -- the future only needs what remains.

>>> coin_change([1, 2, 5], 11)
3
>>> coin_change([2], 3)
-1
>>> coin_change([1], 0)
0
>>> coin_change([186, 419, 83, 408], 6249)
20
"""

# -- prelude --
def memo(f):                                # unbounded memoizer; enough for DP (no eviction by design)
    cache = {}
    def wrapped(*args, **kw):
        key = (args, frozenset(kw.items())) if kw else args
        if key not in cache:
            cache[key] = f(*args, **kw)
        return cache[key]
    wrapped.cache = cache                   # peek at the DP table if curious
    return wrapped

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_coin_change: {r.attempted - r.failed}/{r.attempted} doctests passing")
