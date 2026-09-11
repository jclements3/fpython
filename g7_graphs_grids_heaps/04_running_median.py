"""04_running_median -- Median after each arrival.

Even counts average the two middle values; one decimal is the
caller's problem -- return floats.

Contract:
    running_median(xs: list[int]) -> list[float]

Hint:
    Two heaps: lo holds the lower half NEGATED (the prelude heap is
    min-only), hi the upper half. Push through lo into hi, rebalance
    so lo keeps the extra; the median reads off the tops.

>>> running_median([12, 4, 5, 3, 8, 7])
[12.0, 8.0, 5.0, 4.5, 5.0, 6.0]
>>> running_median([10])
[10.0]
>>> running_median([1, 2, 3, 4])
[1.0, 1.5, 2.0, 2.5]
"""

# -- prelude --
def heappush(h, x):                         # min-heap on a plain list: sift-up
    h.append(x)
    i = len(h) - 1
    while i and h[(i - 1) // 2] > h[i]:
        h[(i - 1) // 2], h[i] = h[i], h[(i - 1) // 2]
        i = (i - 1) // 2

def heappop(h):                             # min-heap on a plain list: sift-down
    h[0], h[-1] = h[-1], h[0]
    top = h.pop()
    i, n = 0, len(h)
    while True:
        s, l, r = i, 2*i + 1, 2*i + 2
        if l < n and h[l] < h[s]: s = l
        if r < n and h[r] < h[s]: s = r
        if s == i:
            return top
        h[i], h[s] = h[s], h[i]
        i = s

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"04_running_median: {r.attempted - r.failed}/{r.attempted} doctests passing")
