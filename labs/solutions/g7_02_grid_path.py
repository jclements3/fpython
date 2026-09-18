"""02_grid_path -- Shortest path through a grid.

Steps from top-left to bottom-right through '.' cells, around '#'
walls, moving orthogonally. -1 if unreachable (or an endpoint is a
wall); a 1x1 open grid is 0.

Contract:
    grid_path(grid: list[str]) -> int

Hint:
    BFS: the prelude deque is the frontier, neighbors4 the edges.
    Mark seen when you ENQUEUE, not when you pop.

>>> grid_path(["..", ".."])
2
>>> grid_path([".#", "#."])
-1
>>> grid_path(["."])
0
>>> grid_path(["..#", "#.#", "#.."])
4
"""

# -- prelude --
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

def neighbors4(r, c, R, C):                 # in-bounds orthogonal neighbors
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if 0 <= r + dr < R and 0 <= c + dc < C:
            yield r + dr, c + dc

# solution goes here
def grid_path(grid):
    R, C = len(grid), len(grid[0])
    if grid[0][0] == "#" or grid[R - 1][C - 1] == "#":
        return -1
    q, seen = deque([(0, 0, 0)]), {(0, 0)}
    while len(q):
        r, c, d = q.popleft()
        if (r, c) == (R - 1, C - 1):
            return d
        for nr, nc in neighbors4(r, c, R, C):
            if grid[nr][nc] == "." and (nr, nc) not in seen:
                seen.add((nr, nc))
                q.append((nr, nc, d + 1))
    return -1


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_grid_path: {r.attempted - r.failed}/{r.attempted} doctests passing")
