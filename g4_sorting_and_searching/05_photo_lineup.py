"""05_photo_lineup -- The reported Anduril prompt, prelude-sized.

Back row and front row, same length; can the columns be arranged so
every back person is STRICTLY taller than the front person?

Contract:
    can_lineup(back: list[int], front: list[int]) -> bool

Hint:
    Sort both rows; all over zipWith (>). Be ready to argue why
    sorted-vs-sorted decides it (the exchange argument).

>>> can_lineup([5, 1, 3], [2, 4, 0])
True
>>> can_lineup([1, 2, 3], [1, 2, 3])
False
>>> can_lineup([10, 9], [1, 2])
True
>>> can_lineup([2], [3])
False
"""

# -- prelude --
zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_photo_lineup: {r.attempted - r.failed}/{r.attempted} doctests passing")
