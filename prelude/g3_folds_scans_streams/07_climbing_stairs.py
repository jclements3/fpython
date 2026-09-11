"""07_climbing_stairs -- NeetCode: Climbing Stairs.

Contract:
    climb_stairs(n: int) -> int
    Ways to reach step n taking 1 or 2 steps. n >= 1.

Hint:
    Fibonacci in disguise. iterate the pair step, take the nth --
    an unfold consumed by indexing, no table needed.

>>> climb_stairs(1)
1
>>> climb_stairs(2)
2
>>> climb_stairs(5)
8
>>> climb_stairs(45)
1836311903
"""

# -- prelude --
fst  = lambda p: p[0]

snd  = lambda p: p[1]

last      = lambda xs: xs[-1]

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


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"07_climbing_stairs: {r.attempted - r.failed}/{r.attempted} doctests passing")
