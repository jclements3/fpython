"""06_merge_sort -- A real O(n log n) sort, by hand.

No sorted(), no .sorted().

Contract:
    merge_sorted(xs: list) -> list  (new list; stable)

Hint:
    splitAt the midpoint, recurse on both halves, and the prelude's
    merge does the two-pointer join. Also retype merge itself from
    memory once -- it's the loop interviews ask for.

>>> merge_sorted([5, 2, 8, 1])
[1, 2, 5, 8]
>>> merge_sorted([])
[]
>>> merge_sorted([3, 3, 1])
[1, 3, 3]
>>> merge_sorted([1])
[1]
"""

# -- prelude --
splitAt   = lambda n, xs: (xs[:n], xs[n:]) if n >= 0 else (xs[:0], xs)   # n<0 splits at the front

def merge(a, b):                            # merge two sorted lists, stable; the heart of merge sort
    out, i, j = [], 0, 0                    # (section 13's merge_lists is this same loop on ListNodes)
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return out + a[i:] + b[j:]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"06_merge_sort: {r.attempted - r.failed}/{r.attempted} doctests passing")
