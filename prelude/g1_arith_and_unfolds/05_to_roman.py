"""05_to_roman -- Integer to Roman numeral, 1 <= n <= 3999.

Contract:
    to_roman(n: int) -> str

Hint:
    A left fold over the value table (subtractive pairs included:
    900 'CM', 40 'XL', ...) carrying (remaining, out): each step
    appends sym * (remaining // val) and keeps remaining % val.

>>> to_roman(1994)
'MCMXCIV'
>>> to_roman(9)
'IX'
>>> to_roman(58)
'LVIII'
>>> to_roman(3000)
'MMM'
>>> to_roman(1)
'I'
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
    print(f"05_to_roman: {r.attempted - r.failed}/{r.attempted} doctests passing")
