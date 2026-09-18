"""03_edit_distance -- Levenshtein distance.

Minimum single-character insertions, deletions, or substitutions
turning a into b.

Contract:
    edit_distance(a: str, b: str) -> int

Hint:
    The alignment DP again -- 02's skeleton with min-of-three plus
    one. Matching heads cost nothing; otherwise pay 1 and recurse on
    the three repairs. memo over the index pair.

>>> edit_distance("kitten", "sitting")
3
>>> edit_distance("", "abc")
3
>>> edit_distance("same", "same")
0
>>> edit_distance("flaw", "lawn")
2
>>> edit_distance("a", "b")
1
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
    print(f"03_edit_distance: {r.attempted - r.failed}/{r.attempted} doctests passing")
