"""04_knapsack -- 0/1 knapsack.

Each (weight, value) item usable at most once; maximize value within
capacity.

Contract:
    knapsack(capacity: int, items: list[tuple[int, int]]) -> int

Hint:
    memo over (i, room): take item i or skip it. Two integers of
    state -- the cache keys on the args tuple, so keep them hashable.

>>> knapsack(10, [(5, 10), (4, 40), (6, 30), (3, 50)])
90
>>> knapsack(0, [(1, 100)])
0
>>> knapsack(5, [])
0
>>> knapsack(3, [(4, 100), (2, 7)])
7
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
    print(f"04_knapsack: {r.attempted - r.failed}/{r.attempted} doctests passing")
