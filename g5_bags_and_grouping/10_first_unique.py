"""10_first_unique -- First non-repeating character.

Contract:
    first_unique(s: str) -> str   # the char, or '_' if none

Hint:
    Three prelude names, one line: Counter the string, find the first
    char whose count is 1, fromMaybe the '_' default. Two passes,
    O(n) -- and find stops at the first hit.

>>> first_unique("swiss")
'w'
>>> first_unique("aabb")
'_'
>>> first_unique("")
'_'
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

fromMaybe = lambda d, x: d if x is None else x  # Data.Maybe: the default for every None-returning tool

# Data.List find: lazy first-match -- folds can't stop early, find can
find      = lambda crit, xs: next((x for x in xs if crit(x)), None)   # first match, else None

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"10_first_unique: {r.attempted - r.failed}/{r.attempted} doctests passing")
