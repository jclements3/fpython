"""prelude.py -- Haskell-style Prelude in pure Python, in pedagogical order.

Pascal discipline: strict define-before-use. Read top to bottom and every name is already defined
when you meet it. Sections build on each other:

   1 combinators          2 pairs                3 arithmetic
   4 list basics          5 higher-order lists   6 folds
   7 scans                8 streams (lazy)       9 slicing & spans
  10 sorting & searching 11 strings             12 containers
  13 nodes               14 grids & windows     15 control
  16 monoids & monads

Within a section names run alphabetically, except that a definition is hoisted ahead of the first
name that uses it (foldl before compose, span before break_), so the discipline holds inside
sections too.

Import qualified (import prelude as P): Haskell names shadow builtins by design. Beyond the Prelude
proper: the working parts of Data.List, Data.Map, Data.Maybe, Data.Function and friends are folded
into the same sections -- grouped by what they do, not by the module they came from. None is
Nothing throughout. foldr = foldl(flip(f), reversed(xs), base): iterative, stack-safe, valid only
because Python is strict.
"""

# ============ 1. combinators ============ (functions about functions)

const     = lambda x: lambda _: x                     # always returns x, ignoring the second argument
# curry: converts a two-argument function into a chain of two one-argument functions, so instead
# of calling f(x, y), you call curry(f)(x)(y).
curry     = lambda f: lambda x: lambda y: f(x, y)
flip      = lambda f: (lambda x, y: f(y, x))          # flip f x y = f y x
NOTHING   = object()                                  # Maybe's Nothing: "no arg given"; test with `is`
                                                       # hoisted ahead of foldl, which needs it as a sentinel

def foldl(f, xs, base=NOTHING):  # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if base is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = base
    for x in it:
        acc = f(acc, x)
    return acc

foldr   = lambda f, xs, base: foldl(flip(f), reversed(list(xs)), base)  # THE right fold, via foldl
compose = lambda *fns: lambda x: foldr(lambda f, acc: f(acc), fns, x)   # foldr (.) id: RIGHTMOST first
fromMaybe = lambda d, x: d if x is None else x        # Data.Maybe: default for every None-returning tool
id        = lambda x: x                               # shadows builtin id() by design
isJust    = lambda x: x is not None                   # Data.Maybe: None test as a handable predicate
isNothing = lambda x: x is None                        # Data.Maybe: true when x is Nothing (None)
on        = lambda f, g: lambda x, y: f(g(x), g(y))   # Data.Function: combine via a key -- cmp `on` fst
partial   = lambda f, *bound: lambda *args: f(*bound, *args)   # fix leading args of f, wait for the rest
uncurry   = lambda f: lambda p: f(*p)                  # inverse of curry: call f with a pair, not two args

# ============ 2. pairs ============

fst  = lambda p: p[0]                    # first element of a pair
snd  = lambda p: p[1]                    # second element of a pair
swap = compose(tuple, reversed)   # Data.Tuple

# ============ 3. arithmetic & logic ============

add       = lambda a, b: a + b                                           # (+) as a value: scanl1(add, xs)
div       = lambda a, b: a // b                                          # floors, like Haskell div
even      = lambda n: n % 2 == 0                                         # true for even numbers
gcd       = lambda a, b: abs(a) if b == 0 else gcd(b, a % b)             # >= 0 like Haskell; depth <= 90
halve     = lambda n: n // 2          # e.g. iterate(halve, 1024) -> 1024, 512, 256, ...
hypot     = lambda x, y: (x*x + y*y) ** 0.5                              # straight-line distance

def isqrt(n):  # floor sqrt without floats (Newton)
    if n < 0:
        raise ValueError("isqrt of negative")
    x = n
    y = halve(x + 1)
    while y < x:
        x, y = y, halve(y + n // y)
    return x if n else 0

lcm       = lambda a, b: abs(a // gcd(a, b) * b) if a and b else 0       # >= 0 like Haskell
mod       = lambda a, b: a % b                                           # remainder, sign follows b
mul       = lambda a, b: a * b                                           # (*) as a value: Product, zipWith(mul, a, b)
not_      = lambda b: not b                                              # `not` is a Python keyword
odd       = lambda n: n % 2 == 1                                         # true for odd numbers
otherwise = True                                                        # guard fallback: always true
pred      = lambda x: chr(ord(x) - 1) if isinstance(x, str) else x - 1   # Enum: numbers and Chars
quot      = lambda a, b: -(-a // b) if (a < 0) != (b < 0) else a // b    # truncates, like Haskell quot
rem       = lambda a, b: a - b * quot(a, b)                              # remainder, sign follows a
quotRem   = lambda a, b: (quot(a, b), rem(a, b))                         # (quot, rem) in one call
signum    = lambda x: (x > 0) - (x < 0)                                  # -1, 0, or 1 by the sign of x
sub       = lambda a, b: a - b                                           # (-) as a value: zipWith(sub, a, b)
succ      = lambda x: chr(ord(x) + 1) if isinstance(x, str) else x + 1   # next: increments, advances chars

# ============ 4. list basics ============

drop        = lambda n, xs: list(xs)[max(n, 0):]                           # finite lists; n<0 drops none
elem        = lambda x, xs: x in xs                                        # true if x is in xs
zip_        = lambda a, b: list(zip(a, b))                                 # shortest wins, any iterable
enum        = lambda xs, start=0: zip_(list(range(start, start + len(xs))), xs)  # pairs each x with its index
head        = lambda xs: xs[0]                                             # first element
init        = lambda xs: xs[:-1]                                           # all but the last element
isPrefixOf  = lambda p, xs: list(xs[:len(p)]) == list(p)                   # Data.List; strings or lists
isSuffixOf  = lambda p, xs: list(xs[len(xs) - len(p):]) == list(p)         # not [-len(p):]: [-0:] is ALL
last        = lambda xs: xs[-1]                                            # last element
lookup      = lambda k, pairs: next((v for kk, v in pairs if kk == k), None)   # Nothing -> None
notElem     = lambda x, xs: x not in xs                                    # true if x is not in xs
nub         = compose(list, dict.fromkeys)                                 # unique; first seen wins
null        = lambda xs: len(xs) == 0                                      # true for an empty list
pairwise    = lambda xs: zip_(xs, xs[1:])                                  # zip xs (tail xs)
replicate   = lambda n, x: [x] * n                                         # x repeated n times
splitAt     = lambda n, xs: (xs[:n], xs[n:]) if n >= 0 else (xs[:0], xs)   # n<0 splits at the front
stripPrefix = lambda p, xs: xs[len(p):] if isPrefixOf(p, xs) else None     # Just the rest, or Nothing
tail        = lambda xs: xs[1:]                                            # all but the first element
def transpose(xss):                    # Data.List: rows <-> cols, RAGGED-SAFE like Haskell
    xss = [list(xs) for xs in xss]     # any iterables in (rows may be one-shot); materialise once
    n = max(map(len, xss), default=0)  # short rows just drop out of later columns (no truncation)
    return [[xs[i] for xs in xss if i < len(xs)] for i in range(n)]
unzip       = lambda ps: tuple(map(list, zip(*ps))) if ps else ([], [])    # inverse of zip: pairs -> two lists
zip3        = lambda a, b, c: list(zip(a, b, c))                           # zip three lists together

# ============ 5. higher-order lists ============

filter_   = lambda cond, xs: [x for x in xs if cond(x)]               # keep elements where cond holds
catMaybes = partial(filter_, isJust)                                  # mapMaybe id
concat    = lambda xss: [x for xs in xss for x in xs]                 # flatten one level of nesting
concatMap = lambda f, xs: [y for x in xs for y in f(x)]               # map f over xs, then flatten
cross     = lambda a, b: [(x, y) for x in a for y in b]               # cartesian; `product` is the fold
# Data.List find: lazy first-match -- folds can't stop early, find can
find      = lambda cond, xs: next((x for x in xs if cond(x)), None)   # first match, else None
map_      = lambda f, xs: [f(x) for x in xs]                          # apply f to every element
# Data.Maybe mapMaybe: map and drop the Nothings in ONE pass -- the parse-and-filter shape
mapMaybe  = lambda f, xs: [y for y in (f(x) for x in xs) if y is not None]
def partition(cond, xs):                   # (keepers, rest) in ONE pass; cond called once per element
    yes, no = [], []
    for x in xs:
        (yes if cond(x) else no).append(x)
    return (yes, no)
starmap   = lambda f, pairs: [f(*p) for p in pairs]                   # map . uncurry
zipWith   = lambda f, a, b: [f(x, y) for x, y in zip(a, b)]           # combine two lists elementwise
zipWith3  = lambda f, a, b, c: [f(x, y, z) for x, y, z in zip(a, b, c)]  # combine three lists elementwise

# ============ 6. folds ============ (collapse a list to one value)
# foldl, foldr and compose are hoisted up to section 1 (combinators): compose needs foldr, foldr needs
# foldl, and swap (section 2) needs compose -- so all three must exist before section 2 even begins.

foldl1  = foldl                                                         # foldl seeded by the first element
foldr1  = lambda f, xs: foldl(flip(f), reversed(list(xs)))              # foldr seeded by the last element
product = lambda xs: foldl(mul, xs, 1)                                  # the numeric fold

# enumeration folds -- brute-force licenses for small n (say the bound out loud):
# Control.Monad replicateM: every length-n word over xs -- cross, n times; |xs|^n
replicateM   = lambda n, xs: foldl(lambda acc, _: [s + [x] for s in acc for x in xs], range(n), [[]])
# Data.List subsequences: the powerset; each element DOUBLES acc -- 2^n, fine to n ~ 20
subsequences = lambda xs: foldl(lambda acc, x: acc + [s + [x] for s in acc], list(xs), [[]])

# ============ 7. scans ============ (a fold that keeps its history)

def accumulate(xs, f=None, initial=NOTHING):     # scanl / scanl1
    if f is None:
        f = add
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

scanl  = lambda f, z, xs: list(accumulate(xs, f, initial=z))            # foldl, keeping every accumulator
scanl1 = lambda f, xs: list(accumulate(xs, f))                          # scanl with no explicit base
scanr  = lambda f, z, xs: list(reversed(scanl(flip(f), z, list(reversed(list(xs))))))   # foldr, keeping every acc
scanr1 = lambda f, xs: list(reversed(scanl1(flip(f), list(reversed(list(xs))))))        # scanr with no base

# ============ 8. streams ============ (lazy, possibly infinite)

chain     = lambda *iterables: (x for it in iterables for x in it)   # concat, lazily

def count(start=0, step=1):                 # [start, start+step ..]
    n = start
    while True:
        yield n
        n += step

def cycle(xs):                              # repeat xs forever
    xs = list(xs)
    if not xs:
        raise ValueError("cycle: empty list")   # Haskell errors too; the alternative is a silent hang
    while True:
        yield from xs

def iterate(f, x):                          # iterate f x = [x, f x, f (f x), ..]
    while True:
        yield x
        x = f(x)

def repeat(x, n=None):                      # yield x forever, or n times if given
    if n is None:
        while True:
            yield x
    else:
        for _ in range(n):
            yield x

def unfoldr(f, seed):                       # Data.List unfoldr: f(seed) -> None | (value, seed')
    out = []                                # iterate's finite twin: grows a list until f says stop --
    step = f(seed)                          # no more threading (state, acc) tuples through until
    while step is not None:
        val, seed = step
        out.append(val)
        step = f(seed)
    return out

# ============ 9. slicing & spans ============ (finite views of streams)

def span(cond, xs):                         # split at first failure, ONE pass; safe on one-shot iters
    xs = list(xs)
    i = next((i for i, x in enumerate(xs) if not cond(x)), len(xs))
    return (xs[:i], xs[i:])
break_    = lambda cond, xs: span(compose(not_, cond), xs)             # split at first hit (opposite of span)
chunksOf  = lambda n, xs: [xs[i:i + n] for i in range(0, len(xs), n)]   # Data.List.Split; short last ok

def dropwhile(cond, xs):                    # generator: drop the leading run where cond holds
    it = iter(xs)
    for x in it:
        if not cond(x):
            yield x
            break
    yield from it

dropWhile = lambda cond, xs: list(dropwhile(cond, xs))   # drop the leading run where cond holds, as a list
inits     = lambda xs: [xs[:i] for i in range(len(xs) + 1)]   # Data.List: every prefix, [] first

def islice(iterable, stop):                 # take
    it = iter(iterable)
    for _ in range(stop):
        try:
            yield next(it)
        except StopIteration:
            return

tails     = lambda xs: [xs[i:] for i in range(len(xs) + 1)]   # every suffix; substrings start here
take      = lambda n, xs: list(islice(iter(xs), n))           # works on infinite streams

def takeuntil(cond, xs):                    # like takewhile(not . cond), but INCLUDES the first hit
    for x in xs:
        yield x
        if cond(x):
            return

def takewhile(cond, xs):                    # generator: yield the leading run where cond holds
    for x in xs:
        if not cond(x):
            return
        yield x

takeWhile = lambda cond, xs: list(takewhile(cond, xs))   # take the leading run where cond holds, as a list

# ============ 10. sorting & searching ============

def bisect_left(a, x):                      # first index where a[i] >= x
    lo, hi = 0, len(a)
    while lo < hi:
        mid = halve(lo + hi)
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def bisect_right(a, x):                     # first index where a[i] > x
    lo, hi = 0, len(a)
    while lo < hi:
        mid = halve(lo + hi)
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo

def cmp_to_key(cmp):                        # resurrect Python 2's cmp for sortBy
    class K:
        def __init__(self, x): self.x = x
        def __lt__(self, other): return cmp(self.x, other.x) < 0
    return K

maxOn  = lambda f, xs: max(xs, key=f)      # maximumBy (comparing f) in O(n); first wins ties

def merge(a, b):                            # merge two sorted lists, stable; the heart of merge sort
    out, i, j = [], 0, 0                    # (section 13's merge_lists is this same loop on ListNodes)
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    return out + a[i:] + b[j:]

minOn  = lambda f, xs: min(xs, key=f)      # minimumBy (comparing f): sortOn + head without the sort
sortBy = lambda cmp, xs: sorted(xs, key=cmp_to_key(cmp))   # comparator sort, Python 2 style
sortOn = lambda f, xs: sorted(xs, key=f)   # sortOn (schwartzian, f called once per element)

# ============ 11. strings ============

lines   = str.splitlines                              # split on newlines
unlines = lambda ls: "".join(l + "\n" for l in ls)     # join lines back with trailing newlines
unwords = " ".join                                     # join words with single spaces
words   = str.split                                    # split on whitespace

# ============ 12. containers ============

# multiset ops on Counters (use .get, not [] -- indexing a Counter autovivifies zeros):
bag_diff  = lambda a, b: {k: a[k] - b[k] for k in a if a[k] > b.get(k, 0)}    # clipped at 0
bag_inter = lambda a, b: {k: v for k in a.keys() & b.keys() if (v := min(a.get(k, 0), b.get(k, 0)))}  # min count per shared key
bag_sub   = lambda a, b: all(b.get(k, 0) >= n for k, n in a.items())          # a <= b (inclusion)
bag_union = lambda a, b: {k: max(a.get(k, 0), b.get(k, 0)) for k in a.keys() | b.keys()}

class defaultdict(dict):                    # dict that manufactures a value via factory() on first miss
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

def fromListWith(f, pairs):                 # Data.Map fromListWith: THE dict-building fold; f(new, old)
    d = {}                                  # like insertWith -- so grouping with concat REVERSES each
    for k, v in pairs:                      # group (the classic Haskell gotcha); use add for counts
        d[k] = f(v, d[k]) if k in d else v
    return d                                # Counter == fromListWith(add) over (x, 1);
                                            # grouping == fromListWith(++) over (k, [v])

def getpath(t, ks, default=None):           # read along ks WITHOUT autovivifying
    for k in ks:
        if not isinstance(t, dict) or k not in t:
            return default
        t = t[k]
    return t

def groupBy(eq, xs):                        # Data.List groupBy: runs of CONSECUTIVE elements; each new
    out = []                                # element is compared via eq against the run's FIRST element,
    for x in xs:                            # exactly like Haskell (span-based) -- not its neighbor
        if out and eq(out[-1][0], x):
            out[-1].append(x)
        else:
            out.append([x])
    return out

group = partial(groupBy, lambda a, b: a == b)   # Data.List group: runs of equals, [[a]] -- no keys

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

def heappush(h, x):                         # min-heap on a plain list: sift-up
    h.append(x)
    i = len(h) - 1
    while i and h[halve(i - 1)] > h[i]:
        h[halve(i - 1)], h[i] = h[i], h[halve(i - 1)]
        i = halve(i - 1)

insertWith = lambda f, k, v, d: {**d, k: f(v, d[k]) if k in d else v}   # Data.Map insertWith: PERSISTENT
                                                                        # (fresh dict); f(new, old)
ITree = lambda: defaultdict(ITree)          # infinitely-nestable defaultdict: a tree that grows on access

def paths(t):                               # cata for Tree/ITree: [(keypath, leaf)]
    # recursion depth = tree height (word length / len(nums)) -- well under the ~1000 limit
    if not isinstance(t, dict) or not t:    # leaf = non-dict value, or empty node
        return [([], t)]
    return [([k] + p, leaf) for k, sub in t.items() for p, leaf in paths(sub)]

leaves = compose(partial(map_, snd), paths)   # every leaf value in a Tree/ITree, in path order

def setpath(t, ks, v):                      # write leaf v at key path ks (autovivifies interior)
    for k in ks[:-1]:
        t = t[k]
    t[ks[-1]] = v                           # NB: clobbers any subtree already at ks

Tree  = lambda depth, leaf: (defaultdict(leaf) if depth == 1        # fixed-depth nested defaultdict;
                             else defaultdict(lambda: Tree(depth - 1, leaf)))  # leaves default to leaf()

unionWith = lambda f, a, b: {**a, **{k: f(a[k], v) if k in a else v for k, v in b.items()}}
                                        # Data.Map unionWith: f(a's value, b's value) on shared keys;
                                        # bag_union == unionWith(max), merge-sum == unionWith(add)

# ============ 13. nodes ============ (the LeetCode givens: binary trees & linked lists)

class ListNode:                             # the LeetCode linked list
    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt

class TreeNode:                             # the LeetCode binary tree
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

from_list = lambda xs: foldr(ListNode, xs, None)   # build; foldr of ListNode

def has_cycle(node):                        # Floyd: fast laps slow iff a cycle exists
    slow = fast = node
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:
            return True
    return False

# tfold: the tree cata -- f(val, l_acc, r_acc), z for the empty tree; recursion depth = tree height
tfold     = lambda f, z, t: z if t is None else f(t.val, tfold(f, z, t.left), tfold(f, z, t.right))
inorder   = partial(tfold, lambda v, l, r: l + [v] + r, [])     # left, root, right

def levelorder(t):                          # BFS: the deque earning its keep
    out, q = [], deque([t] if t else [])
    while len(q):
        n = q.popleft()
        out.append(n.val)
        if n.left:  q.append(n.left)
        if n.right: q.append(n.right)
    return out

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

def middle(node):                           # fast/slow: second middle for even lengths
    slow = fast = node
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
    return slow

postorder = partial(tfold, lambda v, l, r: l + r + [v], [])    # left, right, root
preorder  = partial(tfold, lambda v, l, r: [v] + l + r, [])    # root, left, right

def reverse_list(node):                     # three-pointer; prev is a fold accumulator
    prev = None
    while node:
        node.next, prev, node = prev, node, node.next
    return prev

tdepth    = partial(tfold, lambda _, l, r: 1 + max(l, r), 0)   # height of the tree
to_list   = compose(list, partial(unfoldr, lambda n: None if n is None else (n.val, n.next)))  # ListNode chain -> list
tsize     = partial(tfold, lambda _, l, r: 1 + l + r, 0)       # number of nodes in the tree

# ============ 14. grids & windows ============

def longest_window(xs, valid, push, shed):  # sliding-window skeleton; state lives in the closures
    lo = best = 0
    for hi in range(len(xs)):
        push(xs[hi])
        while not valid():                  # shrink until legal again
            shed(xs[lo])
            lo += 1
        best = max(best, hi - lo + 1)
    return best

def neighbors4(r, c, R, C):                 # in-bounds orthogonal neighbors
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if 0 <= r + dr < R and 0 <= c + dc < C:
            yield r + dr, c + dc

def neighbors8(r, c, R, C):                 # ... plus diagonals
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if (dr or dc) and 0 <= r + dr < R and 0 <= c + dc < C:
                yield r + dr, c + dc

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

def until(cond, f, x):                      # until cond f x — loop, not recursion (unbounded depth)
    while not cond(x):
        x = f(x)
    return x

# ============ 16. monoids & monads ============ (the algebra of folds; failure as a value)

# ---- monoids: an associative op with an identity, reified as the pair (mempty, mappend) --------
Monoid  = lambda empty, op: (empty, op)               # a monoid IS its identity and its combiner
All     = Monoid(True, lambda a, b: a and b)          # mconcat(All, bs)  == all(bs)
Any     = Monoid(False, lambda a, b: a or b)          # mconcat(Any, bs)  == any(bs)
both    = lambda m1, m2: Monoid((m1[0], m2[0]),       # tuple monoid: TWO folds in ONE pass
              lambda a, b: (m1[1](a[0], b[0]), m2[1](a[1], b[1])))
First   = Monoid(None, lambda a, b: b if a is None else a)   # first non-None wins
mconcat = lambda m, xs: foldl(m[1], xs, m[0])         # fold a whole list with the monoid
foldMap = lambda f, m, xs: mconcat(m, [f(x) for x in xs])    # map into the monoid, then mconcat
Last    = Monoid(None, lambda a, b: a if b is None else b)   # last non-None wins
ListM   = Monoid([], add)                             # concat as a monoid
MaxM    = Monoid(float("-inf"), max)                  # identity -inf: max of nothing loses to all
MinM    = Monoid(float("inf"), min)                   # identity inf: min of nothing loses to all
Product = Monoid(1, mul)                              # mconcat(Product, xs) == product(xs)
Sum     = Monoid(0, add)                              # mconcat(Sum, xs)     == sum(xs)

# ---- Maybe monad: chain None-propagating steps without if-ladders -----------------------------
# None is Nothing (file header), so a step cannot return None as a SUCCESS -- the standing caveat.
bind      = lambda x, f: None if x is None else f(x)  # >>= : feed x onward unless it already failed
chainM    = lambda *fs: lambda x: foldl(bind, fs, x)  # Kleisli >=> : LEFTMOST runs first (not compose)
sequenceM = lambda xs: foldr(lambda x, acc: None if x is None or acc is None
                             else [x] + acc, xs, [])  # [Maybe a] -> Maybe [a]: all-or-nothing
traverseM = lambda f, xs: sequenceM([f(x) for x in xs])      # map a failable f, demand every success

# ---- Either: a Maybe that carries WHY it failed ------------------------------------------------
bindE   = lambda x, f: x if x[0] == "err" else f(x[1])       # short-circuit, but keep the message
Ok, Err = lambda v: ("ok", v), lambda e: ("err", e)          # tagged pairs; hoisted ahead of chainE
chainE  = lambda *fs: lambda x: foldl(bindE, fs, Ok(x))      # compose Ok/Err-returning steps
