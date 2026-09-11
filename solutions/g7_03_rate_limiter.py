"""03_rate_limiter -- Sliding-window rate limiter.

A request at time ts is denied when its client already has `limit`
ALLOWED requests in (ts - window, ts]. Denied requests consume no
budget. Timestamps arrive non-decreasing.

Contract:
    rate_limiter(window: int, limit: int,
                 events: list[tuple[int, str]]) -> list[tuple[int, str]]
    The denied (ts, client) pairs, in stream order.

Hint:
    Tree(1, deque): each client's allowed timestamps in a deque. The
    prelude deque has no peek -- evict by popleft, and appendleft the
    survivor back. Each stamp enters and leaves once: O(1) amortized.

>>> rate_limiter(10, 2, [(1, 'alice'), (2, 'alice'), (3, 'alice'),
...                      (5, 'bob'), (12, 'alice'), (13, 'alice')])
[(3, 'alice')]
>>> rate_limiter(5, 3, [(1, 'a'), (2, 'a'), (3, 'a')])
[]
>>> rate_limiter(5, 1, [(1, 'a'), (2, 'b'), (3, 'a'), (7, 'a'), (8, 'b')])
[(3, 'a')]
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

# solution goes here
def rate_limiter(window, limit, events):
    allowed = Tree(1, deque)
    denied = []
    for ts, client in events:
        q = allowed[client]
        while len(q):
            t = q.popleft()
            if t > ts - window:
                q.appendleft(t)
                break
        if len(q) >= limit:
            denied.append((ts, client))
        else:
            q.append(ts)
    return denied


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_rate_limiter: {r.attempted - r.failed}/{r.attempted} doctests passing")
