"""02_autocomplete -- Challenge: prefix trie with completion.

Contract:
    make_trie(words: list[str]) -> ITree
        Letter-by-letter trie; each word terminated by '$' whose leaf
        is the word itself.
    complete(trie, prefix: str) -> list[str]
        All stored words starting with prefix, sorted. A word counts
        as its own completion.

Hint:
    setpath writes each word; getpath descends to the prefix's subtree
    WITHOUT autovivifying (reading an ITree with [] would plant ghost
    branches); paths() harvests every '$' leaf below.
    (No-trie baseline: filter_ + isPrefixOf over the word list, O(n*m)
    per query -- the trie is what repeated queries buy.)

>>> make_trie(["at"]) == {'a': {'t': {'$': 'at'}}}
True
>>> t = make_trie(["cat", "car", "card", "dog", "do"])
>>> complete(t, "ca")
['car', 'card', 'cat']
>>> complete(t, "do")
['do', 'dog']
>>> complete(t, "z")
[]
>>> 'z' in t
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

ITree = lambda: defaultdict(ITree)

def paths(t):                               # cata for Tree/ITree: [(keypath, leaf)]
    # recursion depth = tree height (word length / len(nums)) -- well under the ~1000 limit
    if not isinstance(t, dict) or not t:    # leaf = non-dict value, or empty node
        return [([], t)]
    return [([k] + p, leaf) for k, sub in t.items() for p, leaf in paths(sub)]

def setpath(t, ks, v):                      # write leaf v at key path ks (autovivifies interior)
    for k in ks[:-1]:
        t = t[k]
    t[ks[-1]] = v                           # NB: clobbers any subtree already at ks

def getpath(t, ks, default=None):           # read along ks WITHOUT autovivifying
    for k in ks:
        if not isinstance(t, dict) or k not in t:
            return default
        t = t[k]
    return t

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_autocomplete: {r.attempted - r.failed}/{r.attempted} doctests passing")
