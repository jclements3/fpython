"""11_log_report -- Error report from messy logs.

A well-formed line is "<ts> <LEVEL> <service>: <message...>": LEVEL
in {INFO, WARN, ERROR}, service nonempty and glued to its colon,
message may be empty. Blank lines are ignored; any other non-blank
line is malformed.

Contract:
    error_report(loglines: list[str]) -> (report, malformed_count)
    report = [(service, error_count)] for services with >= 1 ERROR,
    sorted by count desc, then name asc.

Hint:
    THE mapMaybe shape: parse(line) -> (level, service) or None.
    The Nones ARE the malformed count; catMaybes + a filter feed
    Counter; sortOn (-count, name) ranks. Messy input, no raw loops.

>>> logs = ["t1 ERROR api: down", "t2 INFO web: ok", "garbage line",
...         "t3 ERROR api: db", "t4 ERROR web: 500", "t5 WARN api: slow",
...         "t6 DEBUG api: no", "t7 ERROR db missing"]
>>> error_report(logs)
([('api', 2), ('web', 1)], 3)
>>> error_report(["t1 INFO web: ok", "half a line"])
([], 1)
>>> error_report([])
([], 0)
"""

# -- prelude --
filter_   = lambda crit, xs: [x for x in xs if crit(x)]

map_      = lambda f, xs: [f(x) for x in xs]

catMaybes = lambda xs: [x for x in xs if x is not None]                      # mapMaybe id

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

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"11_log_report: {r.attempted - r.failed}/{r.attempted} doctests passing")
