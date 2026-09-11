"""06_pascal -- First n rows of Pascal's triangle.

Contract:
    pascal(n: int) -> list[list[int]]

Hint:
    The triangle is a stream: iterate the row step from [1], where
    next = zipWith (+) (0:row) (row:0) -- the row against itself,
    shifted. take n consumes the stream.

>>> pascal(4)
[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1]]
>>> pascal(1)
[[1]]
>>> pascal(0)
[]
>>> pascal(6)[-1]
[1, 5, 10, 10, 5, 1]
"""

# -- prelude --
zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]

def iterate(f, x):                          # iterate f x = [x, f x, f (f x), ..]
    while True:
        yield x
        x = f(x)

def islice(iterable, stop):                 # take
    it = iter(iterable)
    for _ in range(stop):
        try:
            yield next(it)
        except StopIteration:
            return

take      = lambda n, xs: list(islice(iter(xs), n))           # works on infinite streams

# solution goes here
def pascal(n):
    step = lambda row: zipWith(lambda a, b: a + b, [0] + row, row + [0])
    return take(n, iterate(step, [1]))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"06_pascal: {r.attempted - r.failed}/{r.attempted} doctests passing")
