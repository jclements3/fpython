"""03_next_greater -- First later element that's larger.

For each element, the next strictly greater element to its right;
-1 if none.

Contract:
    next_greater(xs: list[int]) -> list[int]

Hint:
    The MONOTONIC stack: fold over enum(xs); the newcomer pops every
    stacked index whose value it beats (that newcomer is their
    answer), then pushes itself. Each index pushes and pops at most
    once -- O(n) despite the inner while. The pro tier of stacks.

>>> next_greater([2, 1, 2, 4, 3])
[4, 2, 4, -1, -1]
>>> next_greater([5, 4, 3])
[-1, -1, -1]
>>> next_greater([])
[]
"""

# -- prelude --
zip_      = lambda a, b: list(zip(a, b))          # shortest wins, any iterable

enum      = lambda xs, start=0: zip_(list(range(start, start + len(xs))), xs)

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

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_next_greater: {r.attempted - r.failed}/{r.attempted} doctests passing")
