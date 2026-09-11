"""01_two_sum -- NeetCode: Two Sum.

Contract:
    two_sum(nums: list[int], target: int) -> tuple[int, int]
    Return indices (i, j), i < j, with nums[i] + nums[j] == target.
    Exactly one solution exists. len(nums) >= 2.

Hint:
    A fold over enum(nums) carrying a {value: index} dict.
    The future needs to know: which values have I seen, and where?

>>> two_sum([2, 7, 11, 15], 9)
(0, 1)
>>> two_sum([3, 2, 4], 6)
(1, 2)
>>> two_sum([3, 3], 6)
(0, 1)
"""

# -- prelude --
zip_      = lambda a, b: list(zip(a, b))          # shortest wins, any iterable

enum      = lambda xs, start=0: zip_(list(range(start, start + len(xs))), xs)

# solution goes here
def two_sum(nums, target):
    seen = {}
    for i, x in enum(nums):
        if target - x in seen:
            return (seen[target - x], i)
        seen[x] = i


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_two_sum: {r.attempted - r.failed}/{r.attempted} doctests passing")
