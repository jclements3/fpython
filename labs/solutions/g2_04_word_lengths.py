"""04_word_lengths -- Map each word to its length.

Contract:
    word_lengths(sentence: str) -> dict[str, int]
    First-appearance key order; repeats collapse harmlessly.

Hint:
    words splits; zip_ the words against map_ len of them; dict() the
    pairs. Duplicate keys overwrite with the same value -- free dedup.

>>> word_lengths("the quick fox")
{'the': 3, 'quick': 5, 'fox': 3}
>>> word_lengths("go go go")
{'go': 2}
>>> word_lengths("")
{}
"""

# -- prelude --
words   = str.split

map_      = lambda f, xs: [f(x) for x in xs]

zip_      = lambda a, b: list(zip(a, b))          # shortest wins, any iterable

# solution goes here
word_lengths = lambda s: dict(zip_(words(s), map_(len, words(s))))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"04_word_lengths: {r.attempted - r.failed}/{r.attempted} doctests passing")
