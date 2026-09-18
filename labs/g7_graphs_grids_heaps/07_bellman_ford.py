"""07_bellman_ford -- Challenge: shortest paths as a fixed point (negative weights ok).

Contract:
    bellman_ford(edges: list[tuple], src) -> dict | None
    Directed edges (u, v, w); w may be negative. dist[n] = shortest
    distance src -> n, unreachable nodes absent. Returns None if a
    negative cycle is reachable from src (distances then have no
    fixed point -- they diverge to -inf).

Hint:
    Shortest paths ARE a fixed point: dist is the least map satisfying
    dist[v] <= dist[u] + w for every edge. So: relax ALL edges as one
    step function, `until` the map stops changing. Convergence within
    |V| - 1 steps is guaranteed (a shortest path has at most |V| - 1
    edges); a change on step |V| proves a negative cycle. Dijkstra is
    the same relax with a clever ORDER; Bellman-Ford orders nothing
    and pays for it in passes.

>>> bellman_ford([('a','b',1), ('b','c',2), ('a','c',4)], 'a') == {'a': 0, 'b': 1, 'c': 3}
True
>>> bellman_ford([('a','b',5), ('b','c',-4), ('a','c',2)], 'a')['c']
1
>>> bellman_ford([('a','b',1), ('b','c',-3), ('c','b',1), ('b','d',1)], 'a') is None
True
>>> bellman_ford([('x','y',7)], 'y')
{'y': 0}
>>> bellman_ford([('a','b',-2), ('b','a',3)], 'a') == {'a': 0, 'b': -2}
True
"""

# -- prelude --
def until(cond, f, x):                      # until cond f x — loop, not recursion (unbounded depth)
    while not cond(x):
        x = f(x)
    return x

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"07_bellman_ford: {r.attempted - r.failed}/{r.attempted} doctests passing")
