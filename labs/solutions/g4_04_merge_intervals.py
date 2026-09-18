"""04_merge_intervals -- Merge overlapping (and touching) intervals.

Intervals are inclusive [s, e]: [1,2] and [2,3] merge to [1,3].

Contract:
    merge_intervals(intervals: list[list[int]]) -> list[list[int]]
    Result sorted by start.

Hint:
    sortOn fst, then one fold: each interval either extends the
    accumulator's last entry or starts a new one.

>>> merge_intervals([[1, 3], [2, 6], [8, 10], [15, 18]])
[[1, 6], [8, 10], [15, 18]]
>>> merge_intervals([[1, 2], [2, 3]])
[[1, 3]]
>>> merge_intervals([[5, 7], [1, 2], [3, 6]])
[[1, 2], [3, 7]]
>>> merge_intervals([[4, 4]])
[[4, 4]]
"""

# -- prelude --
fst  = lambda p: p[0]

sortOn = lambda f, xs: sorted(xs, key=f)    # sortOn (schwartzian, f called once per element)

NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

def foldl(f, xs, base=NOTHING):           # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if base is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = base
    for x in it:
        acc = f(acc, x)
    return acc

# solution goes here
def merge_intervals(intervals):
    def step(acc, iv):
        s, e = iv
        if acc and s <= acc[-1][1]:
            acc[-1][1] = max(acc[-1][1], e)
        else:
            acc.append([s, e])
        return acc
    return foldl(step, sortOn(fst, [list(iv) for iv in intervals]), [])


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"04_merge_intervals: {r.attempted - r.failed}/{r.attempted} doctests passing")
