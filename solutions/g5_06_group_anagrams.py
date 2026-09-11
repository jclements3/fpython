"""06_group_anagrams -- NeetCode: Group Anagrams.

Contract:
    group_anagrams(words: list[str]) -> list[list[str]]
    Partition words into anagram classes; classes in first-seen order,
    members in input order.

Hint:
    Key = canonical form (sorted letters). Two prelude routes, do
    both: Tree(1, list) with a bare append (autovivification aids the
    write-heavy access), or one fromListWith over (key, [w]) pairs --
    combining old + new, since f receives (new, old); a bare (+)
    would reverse each group. Compare.

>>> group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
>>> group_anagrams([""])
[['']]
>>> group_anagrams(["a"])
[['a']]
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

def fromListWith(f, pairs):                 # Data.Map fromListWith: THE dict-building fold; f(new, old)
    d = {}                                  # like insertWith -- so grouping with concat REVERSES each
    for k, v in pairs:                      # group (the classic Haskell gotcha); use add for counts
        d[k] = f(v, d[k]) if k in d else v
    return d                                # Counter == fromListWith(add) over (x, 1);
                                            # grouping == fromListWith(++) over (k, [v])

# solution goes here
def group_anagrams(words):
    return list(fromListWith(lambda new, old: old + new,
                             [("".join(sorted(w)), [w]) for w in words]).values())


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"06_group_anagrams: {r.attempted - r.failed}/{r.attempted} doctests passing")
