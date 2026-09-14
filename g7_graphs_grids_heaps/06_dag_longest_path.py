"""06_dag_longest_path -- Challenge: longest path in a weighted DAG.

Contract:
    dag_longest(edges: list[tuple]) -> (total: int, path: list)
    Directed acyclic edges (u, v, w). The maximum-weight path anywhere
    in the DAG and its node sequence. Ties broken toward the
    lexically-first end node. Input guaranteed acyclic.

Hint:
    Longest path is NP-hard on general graphs; acyclicity is what
    makes it linear. Kahn's topo sort (indegree fold + deque), then a
    fold over topo order relaxing best[v] = max(best[v], best[u] + w).
    Same skeleton as Dijkstra's relax with max for min and topo order
    replacing the heap -- the LCS-vs-edit-distance move on graphs.
    maxOn best picks the end node; feed it the SORTED nodes so
    ties break lexically.

>>> dag_longest([('a','b',3), ('b','c',4), ('a','c',5)])
(7, ['a', 'b', 'c'])
>>> dag_longest([('s','a',1), ('s','b',5), ('a','t',6), ('b','t',1)])
(7, ['s', 'a', 't'])
>>> dag_longest([('u','v',2)])
(2, ['u', 'v'])
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

class deque:                                # two-stack; all four ends amortized O(1)
    def __init__(self, xs=()):
        self._in, self._out = [], list(reversed(list(xs)))
    def append(self, x): self._in.append(x)
    def appendleft(self, x): self._out.append(x)
    def pop(self):
        if not self._in:
            self._in, self._out = list(reversed(self._out)), []
        return self._in.pop()
    def popleft(self):
        if not self._out:
            self._out, self._in = list(reversed(self._in)), []
        return self._out.pop()
    def __len__(self): return len(self._in) + len(self._out)
    def __iter__(self): return iter(self._out[::-1] + self._in)

def iterate(f, x):                          # iterate f x = [x, f x, f (f x), ..]
    while True:
        yield x
        x = f(x)

def takewhile(crit, xs):
    for x in xs:
        if not crit(x):
            return
        yield x

takeWhile = lambda p, xs: list(takewhile(p, xs))

maxOn  = lambda f, xs: max(xs, key=f)    # (minimumBy/maximumBy + comparing; first wins ties)

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"06_dag_longest_path: {r.attempted - r.failed}/{r.attempted} doctests passing")
