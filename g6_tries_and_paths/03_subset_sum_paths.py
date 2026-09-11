"""03_subset_sum_paths -- Challenge: all paths in the decision tree summing to a total.

Contract:
    build_tree(nums: list[int], total: int) -> tree
        The take/skip decision tree over nums. Node = dict with keys
        ('take', x) and ('skip', x); leaf = bool (True iff the takes
        along that path sum to total).
    tree_paths(tree) -> list[list[int]]
        The taken values along every path ending in True, take-first
        DFS order.
    sum_paths(nums: list[int], total: int) -> list[list[int]]
        Every subsequence of nums summing to total. Negatives allowed,
        so a path only ends at full depth -- rem == 0 mid-path proves
        nothing.

Hint:
    An unfold builds the tree from seed (nums, remaining); a fold over
    the tree collects paths ending in True. unfold + fold = hylomorphism:
    fuse them and the tree never exists -- but here it is the exhibit.
    2^n leaves: every subset gets judged, exactly once.
    (The prelude now also ships subsequences -- filtering the powerset
    by sum is the same 2^n with the tree left implicit.)

>>> build_tree([], 0)
True
>>> build_tree([5], 5) == {('take', 5): True, ('skip', 5): False}
True
>>> tree_paths(True)
[[]]
>>> tree_paths(False)
[]
>>> tree_paths(build_tree([1, 2], 3))
[[1, 2]]
>>> sum_paths([1, 2, 3], 3)
[[1, 2], [3]]
>>> sum_paths([2, 4, 6, 10], 16)
[[2, 4, 10], [6, 10]]
>>> sum_paths([1, -1, 2], 2)
[[1, -1, 2], [2]]
>>> sum_paths([], 0)
[[]]
>>> sum_paths([1, 1], 2)
[[1, 1]]
"""

# -- prelude --
head      = lambda xs: xs[0]

tail      = lambda xs: xs[1:]

null      = lambda xs: len(xs) == 0

concat    = lambda xss: [x for xs in xss for x in xs]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_subset_sum_paths: {r.attempted - r.failed}/{r.attempted} doctests passing")
