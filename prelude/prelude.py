"""prelude.py -- Haskell-style Prelude in pure Python, in pedagogical order.

Pascal discipline: strict define-before-use. Read top to bottom and every
name is already defined when you meet it. Sections build on each other:

   1 combinators          2 pairs                3 arithmetic
   4 list basics          5 higher-order lists   6 folds
   7 scans                8 streams (lazy)       9 slicing & spans
  10 sorting & searching 11 strings             12 containers
  13 nodes               14 grids & windows     15 control

Import qualified (import prelude as P): Haskell names shadow builtins by design.
Beyond the Prelude proper: the working parts of Data.List, Data.Map, Data.Maybe,
Data.Function and friends are folded into the same sections -- grouped by what
they do, not by the module they came from. None is Nothing throughout.
foldr = foldl(flip(f), reversed(xs), init): iterative, stack-safe, valid only
because Python is strict.
"""

# ============ 1. combinators ============ (functions about functions)

id        = lambda x: x                            # shadows builtin id() by design
const     = lambda x: lambda _: x
flip      = lambda f: (lambda x, y: f(y, x))    # flip f x y = f y x
curry     = lambda f: lambda x: lambda y: f(x, y)
uncurry   = lambda f: lambda p: f(*p)
partial   = lambda f, *bound: lambda *args: f(*bound, *args)
on        = lambda f, g: lambda x, y: f(g(x), g(y))   # Data.Function: combine via a key -- cmp `on` fst
NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)
fromMaybe = lambda d, x: d if x is None else x  # Data.Maybe: the default for every None-returning tool
isJust    = lambda x: x is not None             # Data.Maybe: the None test as a handable predicate
isNothing = lambda x: x is None

# ============ 2. pairs ============

fst  = lambda p: p[0]
snd  = lambda p: p[1]
swap = lambda p: (p[1], p[0])               # Data.Tuple

# ============ 3. arithmetic & logic ============

succ      = lambda x: chr(ord(x) + 1) if isinstance(x, str) else x + 1   # Enum: numbers and Chars
pred      = lambda x: chr(ord(x) - 1) if isinstance(x, str) else x - 1
even      = lambda n: n % 2 == 0
odd       = lambda n: n % 2 == 1
not_      = lambda b: not b                      # `not` is a Python keyword
otherwise = True
signum    = lambda x: (x > 0) - (x < 0)
div       = lambda a, b: a // b                   # floors, like Haskell div
mod       = lambda a, b: a % b
quot      = lambda a, b: -(-a // b) if (a < 0) != (b < 0) else a // b   # truncates, like Haskell quot
rem       = lambda a, b: a - b * quot(a, b)
quotRem   = lambda a, b: (quot(a, b), rem(a, b))
gcd       = lambda a, b: abs(a) if b == 0 else gcd(b, a % b)   # >= 0 like Haskell; depth <= ~90 for i64
lcm       = lambda a, b: abs(a // gcd(a, b) * b) if a and b else 0   # >= 0 like Haskell
hypot     = lambda x, y: (x*x + y*y) ** 0.5

def isqrt(n):                               # floor sqrt without floats (Newton)
    if n < 0:
        raise ValueError("isqrt of negative")
    x = n
    y = (x + 1) // 2
    while y < x:
        x, y = y, (y + n // y) // 2
    return x if n else 0

# ============ 4. list basics ============

head      = lambda xs: xs[0]
tail      = lambda xs: xs[1:]
init      = lambda xs: xs[:-1]
last      = lambda xs: xs[-1]
null      = lambda xs: len(xs) == 0
elem      = lambda x, xs: x in xs
notElem   = lambda x, xs: x not in xs
replicate = lambda n, x: [x] * n
drop      = lambda n, xs: list(xs)[max(n, 0):]                # finite lists only; n<0 drops nothing
splitAt   = lambda n, xs: (xs[:n], xs[n:]) if n >= 0 else (xs[:0], xs)   # n<0 splits at the front
nub       = lambda xs: list(dict.fromkeys(xs))    # unique, first occurrence wins (dicts keep order)
lookup    = lambda k, pairs: next((v for kk, v in pairs if kk == k), None)   # Nothing -> None
zip_      = lambda a, b: list(zip(a, b))          # shortest wins, any iterable
zip3      = lambda a, b, c: list(zip(a, b, c))
unzip     = lambda ps: tuple(map(list, zip(*ps))) if ps else ([], [])
def transpose(xss):                         # Data.List: rows <-> cols, RAGGED-SAFE like Haskell --
    xss = [list(xs) for xs in xss]          # short rows just drop out of later columns (no truncation)
    n = max(map(len, xss), default=0)
    return [[xs[i] for xs in xss if i < len(xs)] for i in range(n)]
enum      = lambda xs, start=0: zip_(list(range(start, start + len(xs))), xs)
pairwise  = lambda xs: list(zip(xs, xs[1:]))              # zip xs (tail xs)
isPrefixOf  = lambda p, xs: list(xs[:len(p)]) == list(p)             # Data.List; strings and lists alike
isSuffixOf  = lambda p, xs: list(xs[len(xs) - len(p):]) == list(p)   # NB not [-len(p):] -- [-0:] is ALL
stripPrefix = lambda p, xs: xs[len(p):] if isPrefixOf(p, xs) else None  # Just the rest, or Nothing

# ============ 5. higher-order lists ============

map_      = lambda f, xs: [f(x) for x in xs]
filter_   = lambda pred, xs: [x for x in xs if pred(x)]
# Data.List find: lazy first-match -- folds can't stop early, find can
find      = lambda pred, xs: next((x for x in xs if pred(x)), None)   # first match, else None
def partition(pred, xs):                   # (keepers, rest) in ONE pass; pred called once per element
    yes, no = [], []
    for x in xs:
        (yes if pred(x) else no).append(x)
    return (yes, no)
# Data.Maybe mapMaybe: map and drop the Nothings in ONE pass -- the parse-and-filter shape
mapMaybe  = lambda f, xs: [y for y in (f(x) for x in xs) if y is not None]
catMaybes = lambda xs: [x for x in xs if x is not None]                      # mapMaybe id
concat    = lambda xss: [x for xs in xss for x in xs]
concatMap = lambda f, xs: [y for x in xs for y in f(x)]
starmap   = lambda f, pairs: [f(*p) for p in pairs]   # map . uncurry
zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]
zipWith3  = lambda f, a, b, c: [f(x, y, z) for x, y, z in zip(a, b, c)]
cross     = lambda a, b: [(x, y) for x in a for y in b]     # cartesian (`product` names the fold)

# ============ 6. folds ============ (collapse a list to one value)

def foldl(f, xs, init=NOTHING):           # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if init is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = init
    for x in it:
        acc = f(acc, x)
    return acc

foldl1  = lambda f, xs: foldl(f, xs)
foldr   = lambda f, xs, init: foldl(flip(f), reversed(list(xs)), init)
foldr1  = lambda f, xs: foldl(flip(f), reversed(list(xs)))
product = lambda xs: foldl(lambda a, x: a * x, xs, 1)   # the numeric fold
def compose(*fns):                          # foldr (.) id -- RIGHTMOST runs first; constant stack depth
    def composed(x):
        for f in reversed(fns):
            x = f(x)
        return x
    return composed

# enumeration folds -- brute-force licenses for small n (say the bound out loud):
# Data.List subsequences: the powerset; each element DOUBLES acc -- 2^n, fine to n ~ 20
subsequences = lambda xs: foldl(lambda acc, x: acc + [s + [x] for s in acc], list(xs), [[]])
# Control.Monad replicateM: every length-n word over xs -- cross, n times; |xs|^n
replicateM   = lambda n, xs: foldl(lambda acc, _: [s + [x] for s in acc for x in xs], range(n), [[]])

# ============ 7. scans ============ (a fold that keeps its history)

def accumulate(xs, f=None, initial=NOTHING):     # scanl / scanl1
    if f is None:
        f = lambda a, b: a + b
    it = iter(xs)
    if initial is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            return
    else:
        acc = initial
    yield acc
    for x in it:
        acc = f(acc, x)
        yield acc

scanl  = lambda f, z, xs: list(accumulate(xs, f, initial=z))
scanl1 = lambda f, xs: list(accumulate(xs, f))
scanr  = lambda f, z, xs: list(reversed(scanl(flip(f), z, list(reversed(list(xs))))))
scanr1 = lambda f, xs: list(reversed(scanl1(flip(f), list(reversed(list(xs))))))

# ============ 8. streams ============ (lazy, possibly infinite)

def count(start=0, step=1):                 # [start, start+step ..]
    n = start
    while True:
        yield n
        n += step

def repeat(x, n=None):
    if n is None:
        while True:
            yield x
    else:
        for _ in range(n):
            yield x

def cycle(xs):
    xs = list(xs)
    if not xs:
        raise ValueError("cycle: empty list")   # Haskell errors too; the alternative is a silent hang
    while True:
        yield from xs

def iterate(f, x):                          # iterate f x = [x, f x, f (f x), ..]
    while True:
        yield x
        x = f(x)

def unfoldr(f, seed):                       # Data.List unfoldr: f(seed) -> None | (value, seed')
    out = []                                # iterate's finite twin: grows a list until f says stop --
    step = f(seed)                          # no more threading (state, acc) tuples through until
    while step is not None:
        val, seed = step
        out.append(val)
        step = f(seed)
    return out

def chain(*iterables):                      # concat
    for it in iterables:
        yield from it

# ============ 9. slicing & spans ============ (finite views of streams)

def islice(iterable, stop):                 # take
    it = iter(iterable)
    for _ in range(stop):
        try:
            yield next(it)
        except StopIteration:
            return

take      = lambda n, xs: list(islice(iter(xs), n))           # works on infinite streams

def takewhile(pred, xs):
    for x in xs:
        if not pred(x):
            return
        yield x

def takeuntil(pred, xs):                    # like takewhile(not . pred), but INCLUDES the first hit
    for x in xs:
        yield x
        if pred(x):
            return

def dropwhile(pred, xs):
    it = iter(xs)
    for x in it:
        if not pred(x):
            yield x
            break
    yield from it

takeWhile = lambda p, xs: list(takewhile(p, xs))
dropWhile = lambda p, xs: list(dropwhile(p, xs))
def span(p, xs):                            # split at first failure, ONE pass; safe on one-shot iters
    xs = list(xs)
    i = next((i for i, x in enumerate(xs) if not p(x)), len(xs))
    return (xs[:i], xs[i:])
break_    = lambda p, xs: span(lambda x: not p(x), xs)
inits     = lambda xs: [xs[:i] for i in range(len(xs) + 1)]   # Data.List: every prefix, [] first
tails     = lambda xs: [xs[i:] for i in range(len(xs) + 1)]   # every suffix; substrings start here
chunksOf  = lambda n, xs: [xs[i:i + n] for i in range(0, len(xs), n)]   # Data.List.Split; short last ok

# ============ 10. sorting & searching ============

sortOn = lambda f, xs: sorted(xs, key=f)    # sortOn (schwartzian, f called once per element)
minOn  = lambda f, xs: min(xs, key=f)    # best by key in O(n) -- sortOn + head without the sort
maxOn  = lambda f, xs: max(xs, key=f)    # (minimumBy/maximumBy + comparing; first wins ties)

def cmp_to_key(cmp):                        # resurrect Python 2's cmp for sortBy
    class K:
        def __init__(self, x): self.x = x
        def __lt__(self, other): return cmp(self.x, other.x) < 0
    return K

sortBy = lambda cmp, xs: sorted(xs, key=cmp_to_key(cmp))   # comparator sort, Python 2 style

def merge(a, b):                            # merge two sorted lists, stable; the heart of merge sort
    out, i, j = [], 0, 0                    # (section 13's merge_lists is this same loop on ListNodes)
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return out + a[i:] + b[j:]

def bisect_left(a, x):                      # first index where a[i] >= x
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def bisect_right(a, x):                     # first index where a[i] > x
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo

# ============ 11. strings ============

words   = str.split
unwords = " ".join
lines   = str.splitlines
unlines = lambda ls: "".join(l + "\n" for l in ls)

# ============ 12. containers ============

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

def insertWith(f, k, v, d):                 # Data.Map insertWith f k v m: PERSISTENT -- returns a new
    out = dict(d)                           # dict untouched; collision -> f(new, old), Haskell order
    out[k] = f(v, out[k]) if k in out else v   # order (new value first)
    return out

def fromListWith(f, pairs):                 # Data.Map fromListWith: THE dict-building fold; f(new, old)
    d = {}                                  # like insertWith -- so grouping with concat REVERSES each
    for k, v in pairs:                      # group (the classic Haskell gotcha); use add for counts
        d[k] = f(v, d[k]) if k in d else v
    return d                                # Counter == fromListWith(add) over (x, 1);
                                            # grouping == fromListWith(++) over (k, [v])

def unionWith(f, a, b):                     # Data.Map unionWith: merge two dicts, f on shared keys
    out = dict(a)                           # f(a's value, b's value) -- Haskell's left/right order
    for k, v in b.items():
        out[k] = f(out[k], v) if k in out else v
    return out                              # one combinator, many merges:
                                            # bag_union == unionWith(max), merge-sum == unionWith(add)

def groupBy(eq, xs):                        # Data.List groupBy: runs of CONSECUTIVE elements; each new
    out = []                                # element is compared via eq against the run's FIRST element,
    for x in xs:                            # exactly like Haskell (span-based) -- not its neighbor
        if out and eq(out[-1][0], x):
            out[-1].append(x)
        else:
            out.append([x])
    return out

group = lambda xs: groupBy(lambda a, b: a == b, xs)   # Data.List group: runs of equals, [[a]] -- no keys

# multiset ops on Counters (use .get, not [] -- indexing a Counter autovivifies zeros):
bag_union = lambda a, b: {k: max(a.get(k, 0), b.get(k, 0)) for k in a.keys() | b.keys()}
bag_inter = lambda a, b: {k: v for k in a.keys() & b.keys() if (v := min(a.get(k, 0), b.get(k, 0)))}
bag_diff  = lambda a, b: {k: a[k] - b[k] for k in a if a[k] > b.get(k, 0)}    # clipped at 0
bag_sub   = lambda a, b: all(b.get(k, 0) >= n for k, n in a.items())          # a <= b (inclusion)

Tree  = lambda depth, leaf: (defaultdict(leaf) if depth == 1
                             else defaultdict(lambda: Tree(depth - 1, leaf)))
ITree = lambda: defaultdict(ITree)

def paths(t):                               # cata for Tree/ITree: [(keypath, leaf)]
    # recursion depth = tree height (word length / len(nums)) -- well under the ~1000 limit
    if not isinstance(t, dict) or not t:    # leaf = non-dict value, or empty node
        return [([], t)]
    return [([k] + p, leaf) for k, sub in t.items() for p, leaf in paths(sub)]

leaves = lambda t: [l for _, l in paths(t)]

def setpath(t, ks, v):                      # write leaf v at key path ks (autovivifies interior)
    for k in ks[:-1]:
        t = t[k]
    t[ks[-1]] = v                           # NB: clobbers any subtree already at ks

def getpath(t, ks, default=None):           # read along ks WITHOUT autovivifying
    for k in ks:
        if not isinstance(t, dict) or k not in t:
            return default
        t = t[k]
    return t

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

def dsu(n):                                 # union-find, path halving; union -> False if already joined
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[ra] = rb
        return True
    return find, union

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

# ============ 13. nodes ============ (the LeetCode givens: binary trees & linked lists)

class TreeNode:                             # the LeetCode binary tree
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def tfold(f, z, t):                         # cata: f(val, l_acc, r_acc); depth = tree height
    return z if t is None else f(t.val, tfold(f, z, t.left), tfold(f, z, t.right))

inorder   = lambda t: tfold(lambda v, l, r: l + [v] + r, [], t)
preorder  = lambda t: tfold(lambda v, l, r: [v] + l + r, [], t)
postorder = lambda t: tfold(lambda v, l, r: l + r + [v], [], t)
tdepth    = lambda t: tfold(lambda _, l, r: 1 + max(l, r), 0, t)
tsize     = lambda t: tfold(lambda _, l, r: 1 + l + r, 0, t)

def levelorder(t):                          # BFS: the deque earning its keep
    out, q = [], deque([t] if t else [])
    while len(q):
        n = q.popleft()
        out.append(n.val)
        if n.left:  q.append(n.left)
        if n.right: q.append(n.right)
    return out

class ListNode:                             # the LeetCode linked list
    def __init__(self, val=0, next=None):
        self.val, self.next = val, next

def from_list(xs):                          # build; foldr of ListNode
    node = None
    for x in reversed(list(xs)):
        node = ListNode(x, node)
    return node

def to_list(node):                          # unfold back to a Python list
    out = []
    while node:
        out.append(node.val)
        node = node.next
    return out

def reverse_list(node):                     # three-pointer; prev is a fold accumulator
    prev = None
    while node:
        node.next, prev, node = prev, node, node.next
    return prev

def middle(node):                           # fast/slow: second middle for even lengths
    slow = fast = node
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

def has_cycle(node):                        # Floyd: fast laps slow iff a cycle exists
    slow = fast = node
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False

def merge_lists(a, b):                      # merge two sorted lists; dummy-head idiom
    dummy = tail_ = ListNode()
    while a and b:
        if a.val <= b.val:
            tail_.next, a = a, a.next
        else:
            tail_.next, b = b, b.next
        tail_ = tail_.next
    tail_.next = a or b
    return dummy.next

# ============ 14. grids & windows ============

def neighbors4(r, c, R, C):                 # in-bounds orthogonal neighbors
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if 0 <= r + dr < R and 0 <= c + dc < C:
            yield r + dr, c + dc

def neighbors8(r, c, R, C):                 # ... plus diagonals
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if (dr or dc) and 0 <= r + dr < R and 0 <= c + dc < C:
                yield r + dr, c + dc

def longest_window(xs, valid, add, rem):    # sliding-window skeleton; state lives in the closures
    lo = best = 0
    for hi in range(len(xs)):
        add(xs[hi])
        while not valid():                  # shrink until legal again
            rem(xs[lo])
            lo += 1
        best = max(best, hi - lo + 1)
    return best

# ============ 15. control ============

def memo(f):                                # unbounded memoizer; enough for DP (no eviction by design)
    cache = {}
    def wrapped(*args, **kw):
        key = (args, frozenset(kw.items())) if kw else args
        if key not in cache:
            cache[key] = f(*args, **kw)
        return cache[key]
    wrapped.cache = cache                   # peek at the DP table if curious
    return wrapped

def until(p, f, x):                         # until p f x — loop, not recursion (unbounded depth)
    while not p(x):
        x = f(x)
    return x
