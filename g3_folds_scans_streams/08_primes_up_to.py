"""08_primes_up_to -- All primes <= n, ascending.

Contract:
    primes_up_to(n: int) -> list[int]

Hint:
    Streams, Haskell style: candidates = takeWhile (<= n) count(2);
    keep p when no divisor in takeWhile (<= isqrt p) count(2) divides
    it -- all over the remainders. (The array sieve is faster; this
    version is about reading streams.)

>>> primes_up_to(20)
[2, 3, 5, 7, 11, 13, 17, 19]
>>> primes_up_to(2)
[2]
>>> primes_up_to(1)
[]
>>> len(primes_up_to(100))
25
"""

# -- prelude --
def count(start=0, step=1):                 # [start, start+step ..]
    n = start
    while True:
        yield n
        n += step

def takewhile(cond, xs):
    for x in xs:
        if not cond(x):
            return
        yield x

takeWhile = lambda p, xs: list(takewhile(p, xs))

filter_   = lambda cond, xs: [x for x in xs if cond(x)]

def isqrt(n):                               # floor sqrt without floats (Newton)
    if n < 0:
        raise ValueError("isqrt of negative")
    x = n
    y = (x + 1) // 2
    while y < x:
        x, y = y, (y + n // y) // 2
    return x if n else 0

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"08_primes_up_to: {r.attempted - r.failed}/{r.attempted} doctests passing")
