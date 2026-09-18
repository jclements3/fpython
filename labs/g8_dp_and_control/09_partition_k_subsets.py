"""09_partition_k_subsets -- LC 698: Partition to K Equal Sum Subsets.

Contract:
    can_partition(nums: list[int], k: int) -> bool
    True iff nums splits into k non-empty groups of equal sum.
    Positive ints, small n (say the bound: 2^n states).

Hint:
    The mask family, pure form: the future needs (which numbers
    remain, how much room is left in the group being filled). When a
    group closes (room hits 0) the room resets to target -- so the
    state is just (used, room): the number of CLOSED groups is
    implied by the used-sum. memo over that pair; fill greedily
    into one group at a time to avoid counting group orderings.
    (g8_06's go is this skeleton plus geometry.)

>>> can_partition([4, 3, 2, 3, 5, 2, 1], 4)
True
>>> can_partition([1, 2, 3, 4], 3)
False
>>> can_partition([2, 2, 2, 2], 2)
True
>>> can_partition([1], 1)
True
>>> can_partition([1, 1], 3)
False
"""

# -- prelude --
def memo(f):                                # unbounded memoizer; enough for DP (no eviction by design)
    cache = {}
    def wrapped(*args, **kw):
        key = (args, frozenset(kw.items())) if kw else args
        if key not in cache:
            cache[key] = f(*args, **kw)
        return cache[key]
    wrapped.cache = cache                   # peek at the DP table if curious
    return wrapped

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"09_partition_k_subsets: {r.attempted - r.failed}/{r.attempted} doctests passing")
