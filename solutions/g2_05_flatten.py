"""05_flatten -- Flatten one level of nesting.

Contract:
    flatten(lists: list[list]) -> list

Hint:
    This IS the prelude's concat. One name, zero work.

>>> flatten([[1, 2], [3], [4, 5]])
[1, 2, 3, 4, 5]
>>> flatten([[], [1], []])
[1]
>>> flatten([])
[]
"""

# -- prelude --
concat    = lambda xss: [x for xs in xss for x in xs]

# solution goes here
flatten = concat


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_flatten: {r.attempted - r.failed}/{r.attempted} doctests passing")
