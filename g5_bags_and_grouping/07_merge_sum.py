"""07_merge_sum -- Merge two dicts of numbers, summing shared keys.

Don't mutate the inputs. Key order: a's keys, then b's new ones.

Contract:
    merge_sum(a: dict, b: dict) -> dict

Hint:
    This IS unionWith with (+): merge, combining shared keys by
    addition. The prelude's bag_union is the SAME merge with max --
    one combinator, different monoid. Spot the difference and say it.
    (fromListWith over the two items() lists concatenated gets there
    too; decide which reads better.)

>>> merge_sum({'a': 1, 'b': 2}, {'b': 3, 'c': 4})
{'a': 1, 'b': 5, 'c': 4}
>>> merge_sum({}, {'x': 1})
{'x': 1}
>>> merge_sum({'x': 1}, {})
{'x': 1}
"""

# -- prelude --
def unionWith(f, a, b):                     # Data.Map unionWith: merge two dicts, f on shared keys
    out = dict(a)                           # f(a's value, b's value) -- Haskell's left/right order
    for k, v in b.items():
        out[k] = f(out[k], v) if k in out else v
    return out                              # one combinator, many merges:
                                            # bag_union == unionWith(max), merge-sum == unionWith(add)

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"07_merge_sum: {r.attempted - r.failed}/{r.attempted} doctests passing")
