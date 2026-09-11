"""10_reverse_words -- Reverse the word order.

Runs of whitespace collapse (that's what a bare split does).

Contract:
    reverse_words(s: str) -> str

Hint:
    An unwords . reverse . words sandwich -- three names, no loop.

>>> reverse_words("the quick brown fox")
'fox brown quick the'
>>> reverse_words("  hello   world  ")
'world hello'
>>> reverse_words("solo")
'solo'
"""

# -- prelude --
words   = str.split

unwords = " ".join

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"10_reverse_words: {r.attempted - r.failed}/{r.attempted} doctests passing")
