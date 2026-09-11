"""07_max_height_cuboids -- LC 1691: Maximum Height by Stacking Cuboids.

Any rotation allowed; cuboid A sits on B only when ALL THREE of A's
dims are <= B's, compared side to side. Each cuboid used at most
once. Maximize stack height.

Contract:
    max_height(cuboids: list[tuple[int, int, int]]) -> int

Hint:
    The rotation freedom COLLAPSES: sort each cuboid's own dims
    ascending -- the biggest dim as height is always at least as good,
    and sorted-vs-sorted is the only comparison that can succeed (the
    photo_lineup exchange argument, twice). Then sort the cuboids and
    run weighted LIS: best ending at i = h_i + best over j fitting
    under i. Fold-with-history, O(n^2) -- the g4_07 shape with sum
    instead of length. (g8_06's mask version is the ground truth
    oracle for THIS file: same >= 17-style surprises, different fit
    rule -- all three dims here, base only there.)

>>> max_height([(50, 45, 20), (95, 37, 53), (45, 23, 12)])
190
>>> max_height([(38, 25, 45), (76, 35, 3)])
76
>>> max_height([(7, 11, 17), (7, 17, 11), (11, 7, 17), (11, 17, 7), (17, 7, 11), (17, 11, 7)])
102
>>> max_height([(1, 1, 1)])
1
"""

# -- prelude --
zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"07_max_height_cuboids: {r.attempted - r.failed}/{r.attempted} doctests passing")
