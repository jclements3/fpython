"""02_lcs -- NeetCode: Longest Common Subsequence.

Contract:
    lcs(a: str, b: str) -> int
    Length of the longest common subsequence (not substring).

Hint:
    Alignment pattern, dp[i][j] -- same skeleton as 03's edit
    distance, but max instead of min. Index-based args for the cache.

>>> lcs("abcde", "ace")
3
>>> lcs("abc", "abc")
3
>>> lcs("abc", "def")
0
>>> lcs("", "abc")
0
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
def lcs(a, b):
    @memo
    def go(i, j):
        if i == len(a) or j == len(b):
            return 0
        if a[i] == b[j]:
            return 1 + go(i + 1, j + 1)
        return max(go(i + 1, j), go(i, j + 1))
    return go(0, 0)


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_lcs: {r.attempted - r.failed}/{r.attempted} doctests passing")
