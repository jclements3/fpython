"""01_is_anagram_sorted -- Anagrams via canonical form.

True when a and b use exactly the same letters, ignoring case and
non-letters. (g5 solves the same problem with bags -- do both, argue
which you'd ship.)

Contract:
    is_anagram(a: str, b: str) -> bool

Hint:
    A canonical form makes equality trivial: sort of the cleaned,
    lowered characters. filter_ str.isalpha does the cleaning.

>>> is_anagram("Listen", "Silent")
True
>>> is_anagram("hello", "world")
False
>>> is_anagram("a gentleman", "elegant man")
True
>>> is_anagram("ab", "abb")
False
"""

# -- prelude --
filter_   = lambda pred, xs: [x for x in xs if pred(x)]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_is_anagram_sorted: {r.attempted - r.failed}/{r.attempted} doctests passing")
