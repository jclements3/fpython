"""02_count_vowels -- Count vowels, case-insensitive.

Contract:
    count_vowels(s: str) -> int

Hint:
    len . filter_ (in "aeiou") . lower -- a filter consumed by len is
    the counting idiom.

>>> count_vowels("Programming")
3
>>> count_vowels("AEIOU")
5
>>> count_vowels("xyz")
0
>>> count_vowels("")
0
"""

# -- prelude --
filter_   = lambda pred, xs: [x for x in xs if pred(x)]

# solution goes here
count_vowels = lambda s: len(filter_(lambda c: c in "aeiou", s.lower()))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_count_vowels: {r.attempted - r.failed}/{r.attempted} doctests passing")
