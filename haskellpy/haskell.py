"""haskell.py -- the comprehensive Haskell-flavoured toolbox for Python.

One importable vocabulary: the working parts of the Prelude, Data.List,
Data.Maybe, Data.Either, Data.Map, Data.Function, Control.Monad, monoids,
and parser combinators, folded into sections and mastered as one language.

Design rules
  * Where the stdlib already has it, the Haskell name WRAPS the stdlib
    (scanl is itertools.accumulate, memo is functools.cache) -- one
    vocabulary, zero reimplementation.
  * Failure is a value.  Maybe uses the true NOTHING sentinel, so None is
    LEGAL data everywhere; parsers fail with FAIL, and Either carries why.
  * do-notation via generators: `yield` is >>= (linear monads only).
  * Constant stack wherever Haskell would lean on TCO: loops, not recursion.
  * Python keywords and builtins keep prelude.py's underscore convention
    (not_, map_, filter_, zip_); `id` stays Python's -- use identity.
"""
from functools import reduce as _reduce, partial, cache as memo, cmp_to_key
from itertools import accumulate as _acc, islice as _islice, pairwise as _pairwise
from itertools import chain, count, cycle, repeat
from operator import add, sub, mul, not_
from math import gcd, lcm, hypot, isqrt, prod as product
from collections import Counter, defaultdict, deque
from heapq import heappush, heappop, merge as _hmerge
import re as _re

# ============ 1. functions ============
identity = lambda x: x
const    = lambda x: lambda *_: x
flip     = lambda f: lambda a, b: f(b, a)
curry    = lambda f: lambda x: lambda y: f(x, y)
uncurry  = lambda f: lambda p: f(*p)

def compose(*fs):
    """Right-to-left composition, iterative (constant stack).
    >>> compose(str, abs)(-3)
    '3'
    >>> o(str, abs)(-3)
    '3'
    """
    def g(x):
        for f in reversed(fs):
            x = f(x)
        return x
    return g

o = compose                      # ML's operator: o(f, g) is f after g

def pipe(x, *fs):
    """Left-to-right application: pipe(x, f, g) == g(f(x)).
    >>> pipe(-3, abs, str)
    '3'
    """
    for f in fs:
        x = f(x)
    return x

def on(f, g):
    """Data.Function: combine two arguments via a key.
    >>> on(sub, len)('haskell', 'py')
    5
    """
    return lambda x, y: f(g(x), g(y))

# ============ 2. pairs ============
fst  = lambda p: p[0]
snd  = lambda p: p[1]
swap = o(tuple, reversed)

# ============ 3. sentinels ============
class _Sentinel:
    __slots__ = ("_n",)
    def __init__(self, n): self._n = n
    def __repr__(self):    return self._n
    def __bool__(self):    return False

NOTHING = _Sentinel("NOTHING")   # Maybe's Nothing; None is a legal Just here
FAIL    = _Sentinel("FAIL")      # parser failure; (None, rest) is a legal success
_MISS   = _Sentinel("_MISS")     # internal: absent optional argument

# ============ 4. arithmetic & logic ============
# add, sub, mul, not_ are operator's; gcd, lcm, hypot, isqrt, product are math's
div       = lambda a, b: a // b                       # floors, like Haskell div
mod       = lambda a, b: a % b                        # sign follows b
halve     = lambda n: n // 2
even      = lambda n: n % 2 == 0
odd       = lambda n: n % 2 == 1
otherwise = True

def quot(a, b):
    """Truncating division, Haskell quot; rem's sign follows a.
    >>> quotRem(-7, 2)
    (-3, -1)
    """
    return -(-a // b) if (a < 0) != (b < 0) else a // b
rem     = lambda a, b: a - b * quot(a, b)
quotRem = lambda a, b: (quot(a, b), rem(a, b))
signum  = lambda x: (x > 0) - (x < 0)
succ    = lambda x: chr(ord(x) + 1) if isinstance(x, str) else x + 1
pred    = lambda x: chr(ord(x) - 1) if isinstance(x, str) else x - 1

# ============ 5. folds, scans, unfolds ============
def foldl(f, xs, base=_MISS):
    """foldl; seeds with the first element if no base is given.
    >>> foldl(lambda a, b: a - b, [1, 2, 3], 10)
    4
    """
    return _reduce(f, xs) if base is _MISS else _reduce(f, xs, base)

def foldr(f, xs, base):
    """Right fold without recursion.
    >>> foldr(lambda x, acc: [x] + acc, [1, 2, 3], [])
    [1, 2, 3]
    """
    return _reduce(flip(f), reversed(list(xs)), base)

foldl1 = foldl
foldr1 = lambda f, xs: _reduce(flip(f), reversed(list(xs)))

def scanl(f, xs, base=_MISS):
    """All intermediate foldl states (itertools.accumulate).
    >>> scanl(add, [1, 2, 3], 0)
    [0, 1, 3, 6]
    """
    return list(_acc(xs, f) if base is _MISS else _acc(xs, f, initial=base))

scanl1 = lambda f, xs: scanl(f, xs)
scanr  = lambda f, xs, base: scanl(flip(f), reversed(list(xs)), base)[::-1]
scanr1 = lambda f, xs: scanl(flip(f), reversed(list(xs)))[::-1]

def unfoldr(f, seed):
    """Anamorphism: f(seed) -> (value, seed') or NOTHING to stop.
    >>> unfoldr(lambda n: NOTHING if n == 0 else (n, n - 1), 4)
    [4, 3, 2, 1]
    """
    out = []
    while (r := f(seed)) is not NOTHING:
        out.append(r[0]); seed = r[1]
    return out

def until(cond, f, x):
    """Loop f until cond holds.
    >>> until(lambda n: n > 100, lambda n: n * 2, 1)
    128
    """
    while not cond(x):
        x = f(x)
    return x

# brute-force enumerations (say the bound out loud):
replicateM   = lambda n, xs: foldl(lambda acc, _: [s + [x] for s in acc for x in xs], range(n), [[]])   # |xs|^n
subsequences = lambda xs: foldl(lambda acc, x: acc + [s + [x] for s in acc], list(xs), [[]])            # 2^n

# ============ 6. streams ============ (lazy; chain, count, cycle, repeat are itertools')
def iterate(f, x):
    """Infinite stream x, f(x), f(f(x)), ...
    >>> take(5, iterate(lambda n: n * 2, 1))
    [1, 2, 4, 8, 16]
    """
    while True:
        yield x
        x = f(x)

take = lambda n, xs: list(_islice(iter(xs), n))       # safe on infinite streams

# ============ 7. list basics ============
head        = lambda xs: xs[0]
tail        = lambda xs: xs[1:]
init        = lambda xs: xs[:-1]
last        = lambda xs: xs[-1]
drop        = lambda n, xs: list(xs)[max(n, 0):]
splitAt     = lambda n, xs: (xs[:n], xs[n:]) if n >= 0 else (xs[:0], xs)
replicate   = lambda n, x: [x] * n
elem        = lambda x, xs: x in xs
notElem     = lambda x, xs: x not in xs
null        = lambda xs: len(xs) == 0
nub         = o(list, dict.fromkeys)                  # unique, first seen wins
enum        = lambda xs, start=0: list(enumerate(xs, start))
pairwise    = lambda xs: list(_pairwise(xs))
zip_        = lambda a, b: list(zip(a, b))
zip3        = lambda a, b, c: list(zip(a, b, c))
unzip       = lambda ps: tuple(map(list, zip(*ps))) if ps else ([], [])
isPrefixOf  = lambda p, xs: list(xs[:len(p)]) == list(p)
isSuffixOf  = lambda p, xs: list(xs[len(xs) - len(p):]) == list(p)

def lookup(k, pairs):
    """Assoc-list lookup into Maybe (a stored None is data).
    >>> lookup('b', [('a', 1), ('b', None)]) is None
    True
    >>> lookup('c', [('a', 1)]) is NOTHING
    True
    """
    return next((v for kk, v in pairs if kk == k), NOTHING)

def stripPrefix(p, xs):
    """The rest after prefix p, or NOTHING.
    >>> stripPrefix('foo', 'foobar')
    'bar'
    >>> stripPrefix('x', 'foobar') is NOTHING
    True
    """
    return xs[len(p):] if isPrefixOf(p, xs) else NOTHING

# ============ 8. higher-order lists ============
map_      = lambda f, xs: [f(x) for x in xs]
filter_   = lambda cond, xs: [x for x in xs if cond(x)]
concat    = lambda xss: [x for xs in xss for x in xs]
concatMap = lambda f, xs: [y for x in xs for y in f(x)]
cross     = lambda a, b: [(x, y) for x in a for y in b]
starmap   = lambda f, pairs: [f(*p) for p in pairs]
zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]
zipWith3  = lambda f, a, b, c: [f(x, y, z) for x, y, z in zip(a, b, c)]

def find(cond, xs):
    """First match, lazily, into Maybe.
    >>> find(even, [1, 3, 4, 5])
    4
    >>> find(even, [1, 3]) is NOTHING
    True
    """
    return next((x for x in xs if cond(x)), NOTHING)

def partition(cond, xs):
    """(keepers, rest) in ONE pass, cond called once per element.
    >>> partition(even, [1, 2, 3, 4])
    ([2, 4], [1, 3])
    """
    yes, no = [], []
    for x in xs:
        (yes if cond(x) else no).append(x)
    return (yes, no)

# ============ 9. slicing & spans ============
def span(cond, xs):
    """Split at first failure, one pass, one cond call per element.
    >>> span(lambda x: x < 3, [1, 2, 3, 1])
    ([1, 2], [3, 1])
    """
    xs = list(xs)
    i = next((i for i, x in enumerate(xs) if not cond(x)), len(xs))
    return (xs[:i], xs[i:])

break_ = lambda cond, xs: span(o(not_, cond), xs)

def takewhile(cond, xs):                    # generator
    for x in xs:
        if not cond(x):
            return
        yield x

def dropwhile(cond, xs):                    # generator
    it = iter(xs)
    for x in it:
        if not cond(x):
            yield x
            break
    yield from it

def takeuntil(cond, xs):                    # takewhile that INCLUDES the first hit
    for x in xs:
        yield x
        if cond(x):
            return

takeWhile = lambda cond, xs: list(takewhile(cond, xs))
dropWhile = lambda cond, xs: list(dropwhile(cond, xs))
inits     = lambda xs: [xs[:i] for i in range(len(xs) + 1)]
tails     = lambda xs: [xs[i:] for i in range(len(xs) + 1)]

def chunksOf(n, xs):
    """
    >>> chunksOf(2, [1, 2, 3, 4, 5])
    [[1, 2], [3, 4], [5]]
    """
    xs = list(xs)
    return [xs[i:i + n] for i in range(0, len(xs), n)]

def windows(n, xs):
    """Sliding windows of width n.
    >>> windows(3, [1, 2, 3, 4])
    [[1, 2, 3], [2, 3, 4]]
    """
    xs = list(xs)
    return [xs[i:i + n] for i in range(len(xs) - n + 1)]

def groupBy(eq, xs):
    """Haskell semantics: runs anchored on each run's FIRST element.
    >>> groupBy(lambda a, b: a == b, "aabba")
    [['a', 'a'], ['b', 'b'], ['a']]
    """
    out = []
    for x in xs:
        if out and eq(out[-1][0], x):
            out[-1].append(x)
        else:
            out.append([x])
    return out

group = partial(groupBy, lambda a, b: a == b)

def transpose(rows):
    """Ragged-safe like Data.List.
    >>> transpose([[1, 2, 3], [4, 5]])
    [[1, 4], [2, 5], [3]]
    """
    rows = [list(r) for r in rows]
    out, i = [], 0
    while any(i < len(r) for r in rows):
        out.append([r[i] for r in rows if i < len(r)])
        i += 1
    return out

# ============ 10. sorting & searching ============
sortOn = lambda f, xs: sorted(xs, key=f)
sortBy = lambda cmp, xs: sorted(xs, key=cmp_to_key(cmp))
maxOn  = lambda f, xs: max(xs, key=f)
minOn  = lambda f, xs: min(xs, key=f)
merge  = lambda a, b: list(_hmerge(a, b))             # stable merge of sorted lists

# ============ 11. strings ============
lines   = str.splitlines
unlines = lambda ls: "".join(l + "\n" for l in ls)
words   = str.split
unwords = " ".join

# ============ 12. containers ============ (Counter, defaultdict, deque, heappush/heappop are stdlib's)
def fromListWith(f, pairs):
    """Data.Map: THE dict-building fold; f(new, old).
    >>> fromListWith(add, [('a', 1), ('b', 2), ('a', 3)]) == {'a': 4, 'b': 2}
    True
    """
    d = {}
    for k, v in pairs:
        d[k] = f(v, d[k]) if k in d else v
    return d

def insertWith(f, k, v, d):
    """Persistent insert (fresh dict); f(new, old).
    >>> insertWith(add, 'a', 5, {'a': 1}) == {'a': 6}
    True
    """
    return {**d, k: f(v, d[k]) if k in d else v}

def unionWith(f, a, b):
    """Data.Map: merge two dicts, combining shared keys with f.
    >>> unionWith(add, {'a': 1, 'b': 2}, {'b': 3, 'c': 4}) == {'a': 1, 'b': 5, 'c': 4}
    True
    """
    return {k: f(a[k], b[k]) if k in a and k in b else (a[k] if k in a else b[k])
            for k in a.keys() | b.keys()}

def getpath(t, ks, default=NOTHING):
    """Read along a key path without autovivifying; Maybe out.
    >>> getpath({'a': {'b': None}}, ['a', 'b']) is None
    True
    >>> getpath({'a': {}}, ['a', 'b']) is NOTHING
    True
    """
    for k in ks:
        if not isinstance(t, dict) or k not in t:
            return default
        t = t[k]
    return t

# multiset ops on count-dicts (use .get -- indexing a Counter autovivifies):
bag_diff  = lambda a, b: {k: a[k] - b.get(k, 0) for k in a if a[k] > b.get(k, 0)}
bag_inter = lambda a, b: {k: v for k in a.keys() & b.keys() if (v := min(a[k], b[k]))}
bag_union = lambda a, b: {k: max(a.get(k, 0), b.get(k, 0)) for k in a.keys() | b.keys()}
bag_sub   = lambda a, b: all(b.get(k, 0) >= n for k, n in a.items())

# ============ 13. Maybe ============ (NOTHING sentinel; None is a legal value)
def bind(x, f):
    """>>= : short-circuit on NOTHING.
    >>> bind(3, lambda v: v + 1), bind(NOTHING, lambda v: v + 1)
    (4, NOTHING)
    """
    return NOTHING if x is NOTHING else f(x)

isJust    = lambda x: x is not NOTHING
isNothing = lambda x: x is NOTHING
fromMaybe = lambda default, x: default if x is NOTHING else x

listToMaybe = lambda xs: xs[0] if xs else NOTHING
maybeToList = lambda x: [] if x is NOTHING else [x]

def catMaybes(xs):
    """
    >>> catMaybes([1, NOTHING, None, 2])
    [1, None, 2]
    """
    return [x for x in xs if x is not NOTHING]

def mapMaybe(f, xs):
    """Map into Maybe and drop the NOTHINGs, one pass.
    >>> mapMaybe(lambda s: int(s) if s.isdigit() else NOTHING, ['3', 'x', '7'])
    [3, 7]
    """
    return [y for y in map(f, xs) if y is not NOTHING]

def sequenceM(xs):
    """All-or-nothing.
    >>> sequenceM([1, 2]), sequenceM([1, NOTHING])
    ([1, 2], NOTHING)
    """
    out = []
    for x in xs:
        if x is NOTHING:
            return NOTHING
        out.append(x)
    return out

traverseM = lambda f, xs: sequenceM(map_(f, xs))

def maybe_get(d, k):
    """dict lookup into Maybe (None stays distinguishable from missing).
    >>> maybe_get({'a': None}, 'a'), maybe_get({}, 'a')
    (None, NOTHING)
    """
    return d.get(k, NOTHING)

# ============ 14. Either ============ (tagged tuples; match-friendly)
Ok  = lambda v: ("ok", v)
Err = lambda e: ("err", e)

def bindE(x, f):
    """
    >>> bindE(Ok(3), lambda v: Ok(v + 1)), bindE(Err("no"), lambda v: Ok(v))
    (('ok', 4), ('err', 'no'))
    """
    return x if x[0] == "err" else f(x[1])

def sequenceE(xs):
    """First Err wins; else Ok of all values.
    >>> sequenceE([Ok(1), Err("a"), Err("b")])
    ('err', 'a')
    """
    out = []
    for x in xs:
        if x[0] == "err":
            return x
        out.append(x[1])
    return Ok(out)

def traverseE(f, xs):
    """Map into Either, then sequence.
    >>> traverseE(lambda n: Ok(n * 2) if n else Err('zero'), [1, 2])
    ('ok', [2, 4])
    """
    return sequenceE(map_(f, xs))

def partitionEithers(xs):
    """
    >>> partitionEithers([Ok(1), Err('a'), Ok(2)])
    ([1, 2], ['a'])
    """
    oks, errs = [], []
    for tag, v in xs:
        (oks if tag == "ok" else errs).append(v)
    return (oks, errs)

def note(msg, x):
    """Maybe -> Either: attach WHY to a NOTHING.
    >>> note("missing key", NOTHING)
    ('err', 'missing key')
    """
    return Err(msg) if x is NOTHING else Ok(x)

# ============ 15. do-notation ============ (yield is >>=; linear monads only)
def do(binder, is_fail):
    """Build a do-block decorator for any short-circuiting monad."""
    def deco(gen_fn):
        def run(*a, **kw):
            g = gen_fn(*a, **kw)
            def step(val):
                try:
                    m = g.send(val)
                except StopIteration as e:
                    return e.value
                return binder(m, step)
            return step(None)
        return run
    return deco

doM = do(bind,  lambda x: x is NOTHING)     # generator returns a plain value
doE = do(bindE, lambda x: x[0] == "err")    # generator returns Ok(...)/Err(...)

# ============ 16. parser combinators ============
# Parser a = str -> (value, rest) | FAIL.   Values may be None (json null!).
def doP(gen_fn):
    """do-notation that THREADS the input: yield a parser, receive its value.
    Fresh generator per parse -- re-runnable, backtrack-safe under alt."""
    def make(*a, **kw):
        def parser(s):
            g, val = gen_fn(*a, **kw), None
            try:
                while True:
                    r = g.send(val)(s)
                    if r is FAIL:
                        return FAIL
                    val, s = r
            except StopIteration as e:
                return (e.value, s)
        return parser
    return make

def alt(*ps):
    """<|> : first success wins."""
    return lambda s: next((r for r in (p(s) for p in ps) if r is not FAIL), FAIL)

def many(p):
    """Zero or more, loop not recursion; stalls guard against empty matches."""
    def parser(s):
        out = []
        while (r := p(s)) is not FAIL and r[1] != s:
            out.append(r[0]); s = r[1]
        return (out, s)
    return parser

def many1(p):
    def parser(s):
        r = p(s)
        if r is FAIL:
            return FAIL
        rest = many(p)(r[1])
        return ([r[0]] + rest[0], rest[1])
    return parser

def sepBy(p, sep):
    def pair(s):
        r = sep(s)
        return FAIL if r is FAIL else p(r[1])
    def parser(s):
        r = p(s)
        if r is FAIL:
            return ([], s)
        rest = many(pair)(r[1])
        return ([r[0]] + rest[0], rest[1])
    return parser

def lit(c):
    """One expected character, whitespace-blind."""
    def parser(s):
        s = s.lstrip()
        return (c, s[1:]) if s[:1] == c else FAIL
    return parser

def rx(pat, conv=identity):
    """Regex token, whitespace-blind, converted."""
    r = _re.compile(pat)
    def parser(s):
        s = s.lstrip()
        m = r.match(s)
        return (conv(m.group()), s[m.end():]) if m else FAIL
    return parser

def chainl1(p, ops):
    """p (op p)* folded LEFT; ops maps operator char -> binary function."""
    opp = alt(*[lit(c) for c in ops])
    def parser(s):
        vr = p(s)
        while vr is not FAIL:
            op = opp(vr[1])
            if op is FAIL:
                return vr
            w = p(op[1])
            if w is FAIL:
                return vr
            vr = (ops[op[0]](vr[0], w[0]), w[1])
        return FAIL
    return parser

def runParser(p, s):
    """Parser -> Either: Ok(value) or Err showing where it stopped.
    >>> runParser(rx(r'\\d+', int), "42")
    ('ok', 42)
    >>> runParser(rx(r'\\d+', int), "42x")
    ('err', "unconsumed input: 'x'")
    """
    r = p(s)
    if r is FAIL:
        return Err(f"no parse: {s!r}")
    if r[1].strip():
        return Err(f"unconsumed input: {r[1].strip()!r}")
    return Ok(r[0])

# ============ 17. monoids ============
Monoid  = lambda empty, op: (empty, op)
mconcat = lambda m, xs: foldl(m[1], xs, m[0])
foldMap = lambda f, m, xs: mconcat(m, [f(x) for x in xs])
both    = lambda m1, m2: Monoid((m1[0], m2[0]),
              lambda a, b: (m1[1](a[0], b[0]), m2[1](a[1], b[1])))
Sum     = Monoid(0, add)
Product = Monoid(1, mul)
All     = Monoid(True,  lambda a, b: a and b)
Any     = Monoid(False, lambda a, b: a or b)
MaxM    = Monoid(float("-inf"), max)
MinM    = Monoid(float("inf"),  min)
ListM   = Monoid([], add)
First   = Monoid(NOTHING, lambda a, b: b if a is NOTHING else a)
Last    = Monoid(NOTHING, lambda a, b: a if b is NOTHING else b)

if __name__ == "__main__":
    import doctest
    fails, total = doctest.testmod()
    print(f"{total - fails}/{total} doctests passed" if not fails
          else f"{fails} FAILED")
