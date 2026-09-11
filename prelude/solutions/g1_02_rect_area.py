"""02_rect_area -- Rectangle area.

Contract:
    rect_area(w, h) -> w * h  (result type follows the inputs)

Hint:
    Deliberate overkill: area is the numeric fold, product([w, h]).
    See the smallest possible fold once; recognize every fold after.

>>> rect_area(3, 4)
12
>>> rect_area(2.5, 4)
10.0
>>> rect_area(0, 99)
0
"""

# -- prelude --
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

product = lambda xs: foldl(lambda a, x: a * x, xs, 1)   # the numeric fold

# solution goes here
rect_area = lambda w, h: product([w, h])


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_rect_area: {r.attempted - r.failed}/{r.attempted} doctests passing")
