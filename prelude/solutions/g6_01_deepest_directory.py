"""01_deepest_directory -- Challenge: deepest path in a directory forest.

Contract:
    deepest(dirs: list[str]) -> str
    Each string is a '/'-separated path ("a/b/c"). Return the deepest
    full path (unique deepest guaranteed). Paths may share prefixes.

Hint:
    Building IS walking: foldl indexing over the parts autovivifies the
    whole branch -- no setpath needed since there is no leaf value.
    Then one paths() + maxOn keypath length. Note why setpath would
    be WRONG here: writing "a/b" after "a/b/c" would clobber the
    subtree.

>>> deepest(["a/b/c", "a/d", "e"])
'a/b/c'
>>> deepest(["x"])
'x'
>>> deepest(["a/b", "a/b/c/d", "a/b/c"])
'a/b/c/d'
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

NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

def foldl(f, xs, init=NOTHING):           # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if init is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = init
    for x in it:
        acc = f(acc, x)
    return acc

maxOn  = lambda f, xs: max(xs, key=f)    # (minimumBy/maximumBy + comparing; first wins ties)

# solution goes here
def deepest(dirs):
    t = ITree()
    for d in dirs:
        foldl(lambda node, k: node[k], d.split('/'), t)
    return '/'.join(maxOn(lambda pl: len(pl[0]), paths(t))[0])


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_deepest_directory: {r.attempted - r.failed}/{r.attempted} doctests passing")
