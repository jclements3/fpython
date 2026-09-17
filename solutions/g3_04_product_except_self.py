"""04_product_except_self -- NeetCode: Product of Array Except Self.

Contract:
    product_except_self(nums: list[int]) -> list[int]
    out[i] == product of all nums except nums[i]. No division. O(n).
    len(nums) >= 2.

Hint:
    Prefix products = scanl (*) 1, suffix products = scanr (*) 1.
    out = zipWith (*) prefixes suffixes -- offset by one on each side.

>>> product_except_self([1, 2, 3, 4])
[24, 12, 8, 6]
>>> product_except_self([-1, 1, 0, -3, 3])
[0, 0, 9, 0, 0]
"""

# -- prelude --
NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

flip      = lambda f: (lambda x, y: f(y, x))    # flip f x y = f y x

add       = lambda a, b: a + b                                           # (+) as a value: scanl1(add, xs)
mul       = lambda a, b: a * b                                           # (*) as a value: Product, zipWith(mul, a, b)

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

scanl  = lambda f, z, xs: list(accumulate(xs, f, initial=z))

scanr  = lambda f, z, xs: list(reversed(scanl(flip(f), z, list(reversed(list(xs))))))

zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]

# solution goes here
def product_except_self(nums):
    pre = scanl(mul, 1, nums)
    suf = scanr(mul, 1, nums)
    return zipWith(mul, pre[:-1], suf[1:])


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"04_product_except_self: {r.attempted - r.failed}/{r.attempted} doctests passing")
