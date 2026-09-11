"""10_sensor_pairing -- The screen's domain problem, function form.

Two sensor feeds watch the same airspace. A detection is
(id, t, bearing_degrees); ids are sortable strings. Detections a, b
are COMPATIBLE when |a.t - b.t| <= t_tol and their bearing difference
is <= b_tol -- and bearings wrap: 359.5 and 0.3 are 0.8 apart.

Contract:
    pair_detections(a, b, t_tol, b_tol)
        -> (pairs, unpaired_a_ids, unpaired_b_ids)
    Greedy: repeatedly take the lowest-cost compatible pair of still-
    unused detections, cost = |dt| + wrapped bearing diff (exact ties
    by ids). pairs as (a_id, b_id); all three outputs sorted.

Hint:
    Build the compatible candidates as one comprehension over both
    feeds (cost, a_id, b_id, i, j), sort -- the fold that follows
    takes each candidate whose indices are still unused. The wrap is
    min(d, 360 - d) in ONE helper. This is mock_phased.py distilled.

>>> a = [('A0', 10.0, 90.0), ('A1', 20.0, 180.0)]
>>> b = [('B0', 10.2, 91.0), ('B1', 20.1, 179.5)]
>>> pair_detections(a, b, 0.5, 2.0)
([('A0', 'B0'), ('A1', 'B1')], [], [])
>>> pair_detections([('A0', 10.0, 359.5)], [('B0', 10.1, 0.3)], 0.5, 2.0)
([('A0', 'B0')], [], [])
>>> pair_detections([('A0', 0.0, 10.0)], [('B0', 900.0, 200.0)], 0.5, 2.0)
([], ['A0'], ['B0'])
>>> a = [('A0', 10.0, 45.0), ('A1', 30.0, 90.0)]
>>> b = [('B0', 10.5, 44.5), ('B1', 10.6, 46.0), ('B2', 50.0, 200.0)]
>>> pair_detections(a, b, 1.0, 2.0)
([('A0', 'B0')], ['A1'], ['B1', 'B2'])
"""

# -- prelude --
zip_      = lambda a, b: list(zip(a, b))          # shortest wins, any iterable

enum      = lambda xs, start=0: zip_(list(range(start, start + len(xs))), xs)

# solution goes here
def pair_detections(a, b, t_tol, b_tol):
    wrapd = lambda x, y: min(abs(x - y) % 360, 360 - abs(x - y) % 360)
    cands = sorted([(abs(ta - tb) + wrapd(ba, bb), ai, bi, i, j)
                  for i, (ai, ta, ba) in enum(a)
                  for j, (bi, tb, bb) in enum(b)
                  if abs(ta - tb) <= t_tol and wrapd(ba, bb) <= b_tol])
    used_a, used_b, pairs = set(), set(), []
    for _cost, ai, bi, i, j in cands:
        if i not in used_a and j not in used_b:
            used_a.add(i)
            used_b.add(j)
            pairs.append((ai, bi))
    ua = [d[0] for i, d in enum(a) if i not in used_a]
    ub = [d[0] for j, d in enum(b) if j not in used_b]
    return sorted(pairs), sorted(ua), sorted(ub)


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"10_sensor_pairing: {r.attempted - r.failed}/{r.attempted} doctests passing")
