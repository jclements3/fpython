"""03_most_frequent -- Most frequent value; ties -> smallest.

Contract:
    most_frequent(xs: list) -> value

Hint:
    Counter, then minOn the tuple key (-count, value). The
    two-level tie-break lives entirely in the key, and minOn is
    O(n) where sortOn + head pays O(n log n) for the same answer.

>>> most_frequent([1, 2, 2, 3, 3])
2
>>> most_frequent([5, 5, 1])
5
>>> most_frequent([3, 1, 2])
1
>>> most_frequent(["b", "a", "b", "a"])
'a'
"""

# -- prelude --
class defaultdict(dict):
    def __init__(self, factory=None, *args, **kw):
        super().__init__(*args, **kw)
        self.factory = factory
    def __missing__(self, key):
        if self.factory is None:
            raise KeyError(key)
        self[key] = self.factory()
        return self[key]

def Counter(xs):                            # count-by-value; a defaultdict(int) fold
    d = defaultdict(int)
    for x in xs:
        d[x] += 1
    return d

minOn  = lambda f, xs: min(xs, key=f)    # best by key in O(n) -- sortOn + head without the sort

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_most_frequent: {r.attempted - r.failed}/{r.attempted} doctests passing")
