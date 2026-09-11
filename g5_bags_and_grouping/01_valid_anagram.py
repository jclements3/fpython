"""01_valid_anagram -- NeetCode: Valid Anagram.

Contract:
    is_anagram(s: str, t: str) -> bool
    True iff t is a permutation of s. Lowercase ASCII.

Hint:
    Two Counter folds; anagram == equal multisets. (Compare with
    g4's sorted-canonical version: same problem, different algebra.)

>>> is_anagram("anagram", "nagaram")
True
>>> is_anagram("rat", "car")
False
>>> is_anagram("", "")
True
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

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_valid_anagram: {r.attempted - r.failed}/{r.attempted} doctests passing")
