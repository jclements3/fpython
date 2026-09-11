"""04_top_k_words -- The k most frequent words.

Ordered by count descending, ties by word ascending. At least k
distinct words guaranteed.

Contract:
    top_k_words(k: int, text: str) -> list[tuple[str, int]]

Hint:
    Counter over the words, sortOn (-count, word), take k. The whole
    pipeline is three prelude names deep.

>>> top_k_words(2, "the cat the dog the cat bird")
[('the', 3), ('cat', 2)]
>>> top_k_words(3, "b a a b c c")
[('a', 2), ('b', 2), ('c', 2)]
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

def Counter(xs):                            # count-by-value; a defaultdict(int) fold
    d = defaultdict(int)
    for x in xs:
        d[x] += 1
    return d

sortOn = lambda f, xs: sorted(xs, key=f)    # sortOn (schwartzian, f called once per element)

def islice(iterable, stop):                 # take
    it = iter(iterable)
    for _ in range(stop):
        try:
            yield next(it)
        except StopIteration:
            return

take      = lambda n, xs: list(islice(iter(xs), n))           # works on infinite streams

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"04_top_k_words: {r.attempted - r.failed}/{r.attempted} doctests passing")
