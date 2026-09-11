"""01_balanced_brackets -- Matching pairs: valid bracket nesting.

Only ()[]{} appear.

Contract:
    balanced(s: str) -> bool

Hint:
    The stack fold, purest form: a plain list IS a stack, and the
    fold's accumulator is one. The twist worth learning: use None as
    the FAILED state -- once a closer mismatches, the poison
    propagates through the rest of the fold untouched (Maybe as
    accumulator). Balanced == the fold ends on an empty stack.

>>> balanced("([{}])")
True
>>> balanced("([)]")
False
>>> balanced("(((")
False
>>> balanced("")
True
>>> balanced("]")
False
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

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_balanced_brackets: {r.attempted - r.failed}/{r.attempted} doctests passing")
