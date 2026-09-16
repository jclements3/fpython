"""05_dijkstra -- Challenge: shortest paths from weighted (from, to, dist) edges.

Contract:
    dijkstra(edges: list[tuple], src) -> (dist: dict, parent: dict)
        Directed edges (u, v, w), w >= 0. dist[n] = shortest distance
        src -> n; unreachable nodes absent. parent[n] = predecessor on
        one shortest path (parent[src] = None).
    shortest_path(edges, src, dst) -> list | None
        The node sequence of a shortest src -> dst path, None if
        unreachable.

Hint:
    Adjacency map = Tree(1, list) fold over edges. Frontier = the heap.
    Lazy deletion: skip a popped entry unless it matches the current
    best -- the heap may hold stale distances. Path reconstruction =
    an unfold: iterate the parent chain, takeWhile not None, reverse.
    Graphs are not trees -- cycles make tree unfolds diverge, so fold
    over STATES to a fixed point instead.

>>> dist, _ = dijkstra([('a','b',1), ('b','c',2), ('a','c',4)], 'a')
>>> dist == {'a': 0, 'b': 1, 'c': 3}
True
>>> dist, _ = dijkstra([('a','b',5), ('a','c',1), ('c','b',1)], 'a')
>>> dist['b']
2
>>> dijkstra([('x','y',1)], 'y')[0]
{'y': 0}
>>> shortest_path([('a','b',5), ('a','c',1), ('c','b',1)], 'a', 'b')
['a', 'c', 'b']
>>> shortest_path([('a','b',1)], 'a', 'a')
['a']
>>> shortest_path([('a','b',1)], 'b', 'a') is None
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

def iterate(f, x):                          # iterate f x = [x, f x, f (f x), ..]
    while True:
        yield x
        x = f(x)

def takewhile(cond, xs):
    for x in xs:
        if not cond(x):
            return
        yield x

takeWhile = lambda p, xs: list(takewhile(p, xs))

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_dijkstra: {r.attempted - r.failed}/{r.attempted} doctests passing")
