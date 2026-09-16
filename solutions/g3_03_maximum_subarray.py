"""03_maximum_subarray -- NeetCode: Maximum Subarray (Kadane).

Contract:
    max_subarray(nums: list[int]) -> int
    Largest sum of a non-empty contiguous subarray. len(nums) >= 1.

Hint:
    Kadane IS scanl1: best-ending-here = max(x, best_prev + x).
    The scan is the DP table; maximum reads the answer off it.

>>> max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4])
6
>>> max_subarray([1])
1
>>> max_subarray([5, 4, -1, 7, 8])
23
>>> max_subarray([-3, -1, -2])
-1
"""

# -- prelude --
NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

add       = lambda a, b: a + b                                           # (+) as a value: scanl1(add, xs)

def accumulate(xs, f=None, initial=NOTHING):     # scanl / scanl1
    if f is None:
        f = add
    it = iter(xs)
    if initial is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            return
    else:
        acc = initial
    yield acc
    for x in it:
        acc = f(acc, x)
        yield acc

scanl1 = lambda f, xs: list(accumulate(xs, f))

# solution goes here
def max_subarray(nums):
    return max(scanl1(lambda best, x: max(x, best + x), nums))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_maximum_subarray: {r.attempted - r.failed}/{r.attempted} doctests passing")
