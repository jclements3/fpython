"""12_invert_dict -- Swap a dict's keys and values.

Values are unique (so the inversion is lossless).

Contract:
    invert(d: dict) -> dict

Hint:
    A dict is a list of pairs wearing a hat: items(), swap each pair,
    dict() the result. The swap showcase.

>>> invert({'a': 1, 'b': 2})
{1: 'a', 2: 'b'}
>>> invert({})
{}
"""

# -- prelude --
map_      = lambda f, xs: [f(x) for x in xs]

swap = lambda p: (p[1], p[0])               # Data.Tuple

# solution goes here
invert = lambda d: dict(map_(swap, list(d.items())))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"12_invert_dict: {r.attempted - r.failed}/{r.attempted} doctests passing")
