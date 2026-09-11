"""10_min_path_sum -- Cheapest right/down path through a grid.

Contract:
    min_path_sum(grid: list[list[int]]) -> int
    Top-left to bottom-right, moving only right or down.

Hint:
    Grid DP: state (r, c) -- the future only cares where you stand.
    memo over the index pair; base case is the goal cell.
    Compare g7_02: uniform steps there needed BFS; weighted cells
    with only right/down moves make a DAG, so plain DP suffices.

>>> min_path_sum([[1, 3, 1], [1, 5, 1], [4, 2, 1]])
7
>>> min_path_sum([[5]])
5
>>> min_path_sum([[1, 2], [3, 4]])
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
def min_path_sum(grid):
    R, C = len(grid), len(grid[0])

    @memo
    def go(r, c):
        if (r, c) == (R - 1, C - 1):
            return grid[r][c]
        opts = ([go(r + 1, c)] if r + 1 < R else []) + \
               ([go(r, c + 1)] if c + 1 < C else [])
        return grid[r][c] + min(opts)

    return go(0, 0)


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"10_min_path_sum: {r.attempted - r.failed}/{r.attempted} doctests passing")
