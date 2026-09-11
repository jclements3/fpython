"""08_course_schedule -- NeetCode: Course Schedule (cycle detection via Kahn).

Contract:
    can_finish(n: int, prereqs: list[tuple]) -> bool
        Courses 0..n-1; (a, b) means b must precede a. True iff every
        course can be taken, i.e. the prerequisite graph is acyclic.
    find_order(n: int, prereqs: list[tuple]) -> list | None
        A valid course order (smallest-numbered course first on ties),
        or None if impossible.

Hint:
    Kahn's insight inverted: topo sort doesn't FAIL on a cycle, it
    just leaves the cycle behind -- nodes on a cycle never reach
    indegree 0. So: run 06's Kahn, then len(topo) == n is the whole
    cycle test. Heap instead of deque only to make ties deterministic.

>>> find_order(2, [(1, 0)])
[0, 1]
>>> find_order(4, [(1, 0), (2, 0), (3, 1), (3, 2)])
[0, 1, 2, 3]
>>> find_order(2, [(1, 0), (0, 1)]) is None
True
>>> find_order(3, [])
[0, 1, 2]
>>> can_finish(2, [(1, 0)])
True
>>> can_finish(2, [(1, 0), (0, 1)])
False
>>> can_finish(5, [(1, 4), (2, 4), (3, 1), (3, 2)])
True
"""

# -- prelude --
class defaultdict(dict):
    def __init__(self, factory=None, *args, **kw):
        super().__init__(*args, **kw)
        self.factory = factory
    def __missing__(self, key):
        if self.factory is None:
            raise KeyError(key)
        self[key] = self.factory()
        return self[key]

Tree  = lambda depth, leaf: (defaultdict(leaf) if depth == 1
                             else defaultdict(lambda: Tree(depth - 1, leaf)))

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
    print(f"08_course_schedule: {r.attempted - r.failed}/{r.attempted} doctests passing")
