"""04_subset_sum_trie -- Challenge: subset-sum, winners recorded in a solution trie.

Contract:
    solution_trie(nums: list[int], total: int) -> ITree
        Search the take/skip space; write only the WINNING paths (the
        taken values, terminated by '$') into an ITree.
    sum_paths(nums: list[int], total: int) -> list[list[int]]
        The winning paths read back off the trie via paths().
        NB: a trie stores a SET of solutions -- duplicates arising from
        different index choices (e.g. [1, 1] with total 1) collapse to one.
        That is a semantic change from 03's multiset.

Hint:
    The full trio: unfold searches, ITree records, paths() reads.
    Why the '$' terminator? One solution can be a prefix of another
    ([2] inside [2, 4, -4]) -- without an end marker the shorter one
    vanishes into the longer one's interior.

>>> solution_trie([1, 2], 3) == {1: {2: {'$': True}}}
True
>>> sum_paths([1, 2, 3], 3)
[[1, 2], [3]]
>>> sum_paths([2, 4, -4], 2)
[[2, 4, -4], [2]]
>>> sum_paths([1, 1], 1)
[[1]]
>>> sum_paths([], 0)
[[]]
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

# solution goes here
def solution_trie(nums, total):
    t = ITree()
    def go(i, rem, picked):
        if i == len(nums):
            if rem == 0:
                setpath(t, picked + ['$'], True)
            return
        go(i + 1, rem - nums[i], picked + [nums[i]])
        go(i + 1, rem, picked)
    go(0, total, [])
    return t

def sum_paths(nums, total):
    return [p[:-1] for p, _ in paths(solution_trie(nums, total)) if p[-1] == '$']


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"04_subset_sum_trie: {r.attempted - r.failed}/{r.attempted} doctests passing")
