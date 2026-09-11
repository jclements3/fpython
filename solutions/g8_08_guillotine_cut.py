"""08_guillotine_cut -- Max value cut from a sheet, guillotine cuts only.

A W x H sheet; piece types (pw, ph, value), unlimited supply, fixed
orientation (add rotated copies yourself if rotation is allowed).
Every cut runs edge to edge, so each cut splits one rectangle into
two rectangles. Unused offcuts score 0.

Contract:
    guillotine(W: int, H: int, pieces: list[tuple[int, int, int]]) -> int

Hint:
    Guillotine is what re-admits DP: free-form 2D packing has no
    small state (the frontier goes irregular), but edge-to-edge cuts
    keep every subproblem a RECTANGLE -- (w, h), two ints. Interval
    pattern: best(w,h) = max of a piece that fits the sheet EXACTLY,
    every vertical split x, every horizontal split y. A smaller piece
    never needs a direct case: the cut that isolates it is one of the
    splits. memo over (w, h); O(W*H*(W+H)) -- say it.

>>> guillotine(4, 4, [(1, 1, 1)])
16
>>> guillotine(4, 4, [(3, 3, 7), (1, 1, 1)])
16
>>> guillotine(4, 4, [(3, 3, 20), (1, 1, 1)])
27
>>> guillotine(4, 4, [(4, 2, 10), (2, 2, 3)])
20
>>> guillotine(3, 3, [(2, 2, 5)])
5
>>> guillotine(2, 2, [(3, 1, 99)])
0
"""

# -- prelude --
def memo(f):                                # unbounded memoizer; enough for DP (no eviction by design)
    cache = {}
    def wrapped(*args, **kw):
        key = (args, frozenset(kw.items())) if kw else args
        if key not in cache:
            cache[key] = f(*args, **kw)
        return cache[key]
    wrapped.cache = cache                   # peek at the DP table if curious
    return wrapped

# solution goes here
def guillotine(W, H, pieces):
    pieces = list(pieces)

    @memo
    def best(w, h):
        exact  = [v for pw, ph, v in pieces if (pw, ph) == (w, h)]
        vsplit = [best(x, h) + best(w - x, h) for x in range(1, w // 2 + 1)]
        hsplit = [best(w, y) + best(w, h - y) for y in range(1, h // 2 + 1)]
        return max(exact + vsplit + hsplit, default=0)

    return best(W, H)


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"08_guillotine_cut: {r.attempted - r.failed}/{r.attempted} doctests passing")
