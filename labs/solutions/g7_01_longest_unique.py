"""01_longest_unique -- Longest substring without repeats.

Contract:
    longest_unique(s: str) -> int

Hint:
    The longest_window skeleton does the two-pointer bookkeeping; you
    supply the state as closures: per-char counts (Tree(1, int)) plus
    a duplicate tally. valid() == "no duplicates in the window".

>>> longest_unique("abcabcbb")
3
>>> longest_unique("bbbbb")
1
>>> longest_unique("")
0
>>> longest_unique("abba")
2
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

Tree  = lambda depth, leaf: (defaultdict(leaf) if depth == 1
                             else defaultdict(lambda: Tree(depth - 1, leaf)))

def longest_window(xs, valid, push, shed):  # sliding-window skeleton; state lives in the closures
    lo = best = 0
    for hi in range(len(xs)):
        push(xs[hi])
        while not valid():                  # shrink until legal again
            shed(xs[lo])
            lo += 1
        best = max(best, hi - lo + 1)
    return best

# solution goes here
def longest_unique(s):
    counts, dups = Tree(1, int), [0]
    def add(c):
        counts[c] += 1
        dups[0] += counts[c] == 2
    def rem(c):
        counts[c] -= 1
        dups[0] -= counts[c] == 1
    return longest_window(s, lambda: dups[0] == 0, add, rem)


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_longest_unique: {r.attempted - r.failed}/{r.attempted} doctests passing")
