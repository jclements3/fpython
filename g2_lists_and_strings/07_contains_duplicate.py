"""07_contains_duplicate -- NeetCode: Contains Duplicate.

Contract:
    contains_duplicate(nums: list[int]) -> bool
    True iff any value appears at least twice.

Hint:
    nub keeps first occurrences; duplicates exist iff nub shrinks the
    list.

>>> contains_duplicate([1, 2, 3, 1])
True
>>> contains_duplicate([1, 2, 3, 4])
False
>>> contains_duplicate([])
False
"""

# -- prelude --
nub       = lambda xs: list(dict.fromkeys(xs))    # unique, first occurrence wins (dicts keep order)

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"07_contains_duplicate: {r.attempted - r.failed}/{r.attempted} doctests passing")
