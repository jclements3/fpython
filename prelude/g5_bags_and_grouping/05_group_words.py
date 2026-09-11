"""05_group_words -- Group words by first letter.

First-appearance order for both keys and members.

Contract:
    group_words(words: list[str]) -> dict[str, list[str]]

Hint:
    THE fromListWith showcase: pairs (first letter, [word]). The
    combiner receives f(new, old) -- Haskell's order -- so KEEP
    arrival order by combining old + new; a bare (+) would reverse
    each group (the classic Haskell gotcha). Keys keep first-seen
    order.

>>> group_words(["ant", "bee", "ape"])
{'a': ['ant', 'ape'], 'b': ['bee']}
>>> group_words(["cat"])
{'c': ['cat']}
>>> group_words([])
{}
"""

# -- prelude --
def fromListWith(f, pairs):                 # Data.Map fromListWith: THE dict-building fold; f(new, old)
    d = {}                                  # like insertWith -- so grouping with concat REVERSES each
    for k, v in pairs:                      # group (the classic Haskell gotcha); use add for counts
        d[k] = f(v, d[k]) if k in d else v
    return d                                # Counter == fromListWith(add) over (x, 1);
                                            # grouping == fromListWith(++) over (k, [v])

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_group_words: {r.attempted - r.failed}/{r.attempted} doctests passing")
