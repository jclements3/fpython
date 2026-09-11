"""09_lru_class -- An LRU cache class, dict-only.

Capacity at construction; put(key, value); get(key) -> value or None.
Both get and put count as use; puts beyond capacity evict the least
recently used entry.

Contract:
    class LRU(capacity)
        .put(key, value) -> None
        .get(key) -> value | None

Hint:
    The container lesson with no snippet to lean on: dicts remember
    insertion order, so pop + re-insert IS move-to-most-recent, and
    next(iter(d)) is the least recent. That's the whole machine.

>>> c = LRU(2)
>>> c.put('a', 1); c.put('b', 2)
>>> c.get('a')
1
>>> c.put('c', 3)
>>> c.get('b') is None
True
>>> c.get('c')
3
>>> c.get('a')
1
>>> c.put('a', 99); c.get('a')
99
"""

# -- prelude --
# (no snippet needed: the built-in dict, insertion-ordered, IS the container)

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"09_lru_class: {r.attempted - r.failed}/{r.attempted} doctests passing")
