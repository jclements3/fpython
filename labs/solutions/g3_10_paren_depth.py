"""10_paren_depth -- Deepest paren nesting.

Input is balanced, only '(' and ')'.

Contract:
    max_depth(s: str) -> int

Hint:
    Depth is a running total: map each paren to +1/-1, scanl (+) 0
    is the entire depth trace, maximum reads off the answer. No
    stack needed -- the scan IS the stack height's history.

>>> max_depth("(()(()))")
3
>>> max_depth("()()")
1
>>> max_depth("")
0
"""

# -- prelude --
map_      = lambda f, xs: [f(x) for x in xs]

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

scanl  = lambda f, z, xs: list(accumulate(xs, f, initial=z))

# solution goes here
def max_depth(s):
    steps = map_(lambda c: 1 if c == "(" else -1, s)
    return max(scanl(add, 0, steps))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"10_paren_depth: {r.attempted - r.failed}/{r.attempted} doctests passing")
