"""02_ransom_note -- HackerRank: Ransom Note.

Contract:
    can_make(note: list[str], magazine: list[str]) -> bool
    True iff every word in note is available in magazine with at
    least the required multiplicity. Case-sensitive whole words.

Hint:
    Multiset inclusion: Counter(note) <= Counter(magazine), spelled
    as an `all` over the note's counts.

>>> can_make("give me one grand today night".split(), "give me one grand today".split())
False
>>> can_make("two times three is not four".split(), "two times three is not four".split())
True
>>> can_make(["give"], ["Give"])
False
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
    print(f"02_ransom_note: {r.attempted - r.failed}/{r.attempted} doctests passing")
