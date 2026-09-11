"""09_permutations -- All distinct orderings, sorted.

Contract:
    permutations(s: str) -> list[str]

Hint:
    concatMap over the choice of first character: pick s[i], prepend
    it to every permutation of the rest. nub kills duplicates from
    repeated letters; sort at the end.

>>> permutations("abc")
['abc', 'acb', 'bac', 'bca', 'cab', 'cba']
>>> permutations("aab")
['aab', 'aba', 'baa']
>>> permutations("x")
['x']
>>> permutations("")
['']
"""

# -- prelude --
concatMap = lambda f, xs: [y for x in xs for y in f(x)]

nub       = lambda xs: list(dict.fromkeys(xs))    # unique, first occurrence wins (dicts keep order)

# solution goes here
def permutations(s):
    if len(s) <= 1:
        return [s]
    opts = concatMap(
        lambda i: [s[i] + rest for rest in permutations(s[:i] + s[i + 1:])],
        range(len(s)))
    return sorted(nub(opts))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"09_permutations: {r.attempted - r.failed}/{r.attempted} doctests passing")
