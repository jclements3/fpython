CHAPTER = 12
TITLE = "Machines: Deque, DSU, Heap"

ITEMS = [
{
 "id": "12.1", "level": "drill", "title": "Rotate left with a deque",
 "statement": (
  "Write rotate_left(xs, k): rotate a list k positions left using a deque -- popleft feeds\n"
  "append, k times. k may be 0, huge, or applied to an empty list."),
 "contract": "rotate_left(xs: list, k: int) -> list",
 "tests": """>>> rotate_left([1, 2, 3, 4], 1)
[2, 3, 4, 1]
>>> rotate_left([1, 2, 3, 4], 6)
[3, 4, 1, 2]
>>> rotate_left([], 3)
[]
>>> rotate_left([7], 99)
[7]""",
 "solution": """def rotate_left(xs, k):
    d = deque(xs)
    for _ in range(k % len(xs) if xs else 0):
        d.append(d.popleft())
    return list(d)""",
 "note": ("Each rotation is popleft + append, both O(1); k % len caps the work. Common mistake:\n"
          "forgetting the empty-list guard before the modulo."),
},
{
 "id": "12.2", "level": "drill", "title": "Keep only the last k",
 "statement": (
  "A dashboard shows only the k most recent readings. Write last_k(xs, k): feed the stream\n"
  "through a deque, evicting from the front whenever the buffer exceeds k, and return the\n"
  "final buffer as a list."),
 "contract": "last_k(xs: list, k: int) -> list",
 "tests": """>>> last_k([1, 2, 3, 4, 5], 2)
[4, 5]
>>> last_k([1, 2], 5)
[1, 2]
>>> last_k([], 3)
[]""",
 "solution": """def last_k(xs, k):
    d = deque()
    for x in xs:
        d.append(x)
        if len(d) > k:
            d.popleft()
    return list(d)""",
 "note": ("Append at the back, evict from the front: the bounded-buffer idiom, O(1) per event.\n"
          "A plain list doing pop(0) here would be O(n) per eviction."),
},
{
 "id": "12.3", "level": "drill", "title": "Same group yet?",
 "statement": (
  "Write same_group(n, pairs, queries) for elements 0..n-1: apply every merge in pairs, then\n"
  "answer each query (a, b) with whether a and b ended up connected. Compare find results --\n"
  "never raw parent values, which are arbitrary."),
 "contract": "same_group(n: int, pairs: list[tuple], queries: list[tuple]) -> list[bool]",
 "tests": """>>> same_group(5, [(0, 1), (1, 2)], [(0, 2), (0, 3), (3, 3)])
[True, False, True]
>>> same_group(3, [], [(0, 1)])
[False]
>>> same_group(2, [(0, 1)], [(1, 0)])
[True]""",
 "solution": """def same_group(n, pairs, queries):
    f, union = dsu(n)
    for a, b in pairs:
        union(a, b)
    return [f(a) == f(b) for a, b in queries]""",
 "note": ("Union everything, then each query is two finds. Near O(1) per operation with path\n"
          "halving. Naming the local `f` avoids shadowing the prelude's find."),
},
{
 "id": "12.4", "level": "drill", "title": "Heapsort by draining",
 "statement": (
  "Write heap_sorted(xs): push every element onto a min-heap, then pop until empty. The drain\n"
  "order IS sorted order -- that is heapsort."),
 "contract": "heap_sorted(xs: list) -> list",
 "tests": """>>> heap_sorted([5, 1, 4, 1, 3])
[1, 1, 3, 4, 5]
>>> heap_sorted([])
[]
>>> heap_sorted([2])
[2]""",
 "solution": """def heap_sorted(xs):
    h = []
    for x in xs:
        heappush(h, x)
    return [heappop(h) for _ in range(len(h))]""",
 "note": ("n pushes + n pops, each O(log n): O(n log n) total. Duplicates survive -- a heap is\n"
          "a bag, not a set."),
},
{
 "id": "12.5", "level": "drill", "title": "The k smallest",
 "statement": (
  "Write k_smallest(xs, k): the k smallest values in ascending order (all of them if k exceeds\n"
  "the length). Push everything, pop k times."),
 "contract": "k_smallest(xs: list, k: int) -> list",
 "tests": """>>> k_smallest([9, 4, 7, 1, 0], 3)
[0, 1, 4]
>>> k_smallest([5, 5, 5], 2)
[5, 5]
>>> k_smallest([1, 2], 10)
[1, 2]""",
 "solution": """def k_smallest(xs, k):
    h = []
    for x in xs:
        heappush(h, x)
    return [heappop(h) for _ in range(min(k, len(h)))]""",
 "note": ("O(n log n) build, O(k log n) drain -- beats fully sorting when k is small. min(k,\n"
          "len) is the guard the last doctest checks."),
},
{
 "id": "12.6", "level": "apply", "title": "Hot potato",
 "statement": (
  "Players stand in a circle and count around: every m-th player is eliminated until one\n"
  "remains (the Josephus game). Write survivor(names, m): rotate the deque m-1 times\n"
  "(popleft feeding append), eliminate with a popleft, repeat. Return the last name standing."),
 "contract": "survivor(names: list[str], m: int) -> str",
 "tests": """>>> survivor(['a', 'b', 'c', 'd', 'e'], 2)
'c'
>>> survivor(['solo'], 7)
'solo'
>>> survivor(['a', 'b', 'c'], 1)
'c'
>>> survivor(['a', 'b'], 3)
'b'""",
 "solution": """def survivor(names, m):
    d = deque(names)
    while len(d) > 1:
        for _ in range(m - 1):
            d.append(d.popleft())
        d.popleft()
    return d.popleft()""",
 "note": ("The deque IS the circle: rotation moves the count, popleft eliminates. O(n * m).\n"
          "Common mistake: rotating m times instead of m - 1."),
},
{
 "id": "12.7", "level": "apply", "title": "Merge k sorted feeds",
 "statement": (
  "k sensors each emit an already-sorted list of readings. Write merge_all(lists): one sorted\n"
  "stream, heap-powered: seed the heap with each list's head as (value, list_index, position),\n"
  "then repeatedly pop the smallest and push that list's next reading. The index in the tuple\n"
  "breaks value ties so comparison never reaches unorderable data."),
 "contract": "merge_all(lists: list[list[int]]) -> list[int]",
 "tests": """>>> merge_all([[1, 4, 6], [2, 3], [5]])
[1, 2, 3, 4, 5, 6]
>>> merge_all([[], [1], []])
[1]
>>> merge_all([])
[]
>>> merge_all([[1, 1], [1]])
[1, 1, 1]""",
 "solution": """def merge_all(lists):
    h, out = [], []
    for li, xs in enumerate(lists):
        if xs:
            heappush(h, (xs[0], li, 0))
    while h:
        val, li, i = heappop(h)
        out.append(val)
        if i + 1 < len(lists[li]):
            heappush(h, (lists[li][i + 1], li, i + 1))
    return out""",
 "note": ("The heap holds at most one entry per list, so each of the N total readings costs\n"
          "O(log k): O(N log k), the multiway-merge bound. This is the prelude's two-list merge\n"
          "generalised by a frontier."),
},
{
 "id": "12.8", "level": "apply", "title": "How many friend circles?",
 "statement": (
  "n people, a list of friendships. Friendship is transitive through the merges. Write\n"
  "components(n, pairs): how many separate circles remain -- union every pair, then count\n"
  "DISTINCT roots via find over everyone."),
 "contract": "components(n: int, pairs: list[tuple]) -> int",
 "tests": """>>> components(5, [(0, 1), (3, 4)])
3
>>> components(4, [])
4
>>> components(3, [(0, 1), (1, 2)])
1
>>> components(0, [])
0""",
 "solution": """def components(n, pairs):
    f, union = dsu(n)
    for a, b in pairs:
        union(a, b)
    return len({f(i) for i in range(n)})""",
 "note": ("Count roots with a set comprehension over find -- roots are arbitrary but distinct\n"
          "per component. The final full pass of finds also flattens every chain."),
},
{
 "id": "12.9", "level": "apply", "title": "The edge that closes a loop",
 "statement": (
  "Network links arrive one at a time. Write first_cycle_edge(n, edges): the FIRST link that\n"
  "connects two already-connected nodes (union answering False), or None if every link merges\n"
  "something new. This is exactly how Kruskal's algorithm rejects edges."),
 "contract": "first_cycle_edge(n: int, edges: list[tuple]) -> tuple | None",
 "tests": """>>> first_cycle_edge(5, [(0, 1), (1, 2), (0, 2), (3, 4)])
(0, 2)
>>> first_cycle_edge(3, [(0, 1), (1, 2)]) is None
True
>>> first_cycle_edge(2, [(0, 0)])
(0, 0)""",
 "solution": """def first_cycle_edge(n, edges):
    f, union = dsu(n)
    return find(lambda e: not union(e[0], e[1]), edges)""",
 "note": ("find's laziness meets union's side effect: edges are merged one at a time until one\n"
          "reports False, and nothing after it is touched. Keep the dsu locals named f/union so\n"
          "the prelude's find stays visible."),
},
{
 "id": "12.10", "level": "apply", "title": "k-th largest, live",
 "statement": (
  "A leaderboard shows the k-th largest score seen so far, updating per submission. Write\n"
  "kth_largest_stream(xs, k): after each element, report the k-th largest so far, or None\n"
  "while fewer than k have arrived. Keep a min-heap of the k best -- its root IS the answer."),
 "contract": "kth_largest_stream(xs: list[int], k: int) -> list",
 "tests": """>>> kth_largest_stream([3, 1, 5, 12, 2, 11], 3)
[None, None, 1, 3, 3, 5]
>>> kth_largest_stream([4, 4], 1)
[4, 4]
>>> kth_largest_stream([], 2)
[]""",
 "solution": """def kth_largest_stream(xs, k):
    h, out = [], []
    for x in xs:
        heappush(h, x)
        if len(h) > k:
            heappop(h)
        out.append(h[0] if len(h) == k else None)
    return out""",
 "note": ("The bounded min-heap holds the k largest; evicting the MIN keeps exactly them, and\n"
          "h[0] reads the k-th largest in O(1). O(n log k). Common mistake: a max-heap, which\n"
          "cannot evict its smallest."),
},
{
 "id": "12.11", "level": "challenge", "title": "Sliding window maximum",
 "statement": (
  "Write window_max(xs, k): the maximum of every length-k window, in order (classic hard\n"
  "interview question -- O(n) required, so no per-window max()). Keep a deque of INDICES with\n"
  "values decreasing: each newcomer pops smaller values off the back; the front is the\n"
  "window's max, dropped when it slides out of range. The prelude deque has no peek: peek by\n"
  "pop-then-push-back on the side you need."),
 "contract": "window_max(xs: list[int], k: int) -> list[int]",
 "tests": """>>> window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
[3, 3, 5, 5, 6, 7]
>>> window_max([2, 1], 1)
[2, 1]
>>> window_max([4, 2, 3], 3)
[4]
>>> window_max([], 2)
[]""",
 "solution": """def window_max(xs, k):
    d, out = deque(), []                    # indices; values decreasing front to back
    for i, x in enumerate(xs):
        while len(d):
            j = d.pop()                     # peek back = pop, maybe push back
            if xs[j] >= x:
                d.append(j)
                break
        d.append(i)
        f = d.popleft()                     # peek front = popleft, maybe push back
        if f > i - k:
            d.appendleft(f)
        if i >= k - 1:
            f = d.popleft()
            out.append(xs[f])
            d.appendleft(f)
    return out""",
 "note": ("The monotonic deque: every index enters once and leaves once (back-pop when beaten,\n"
          "front-pop when expired), so the nested while is still O(n) amortised. The pop/push-\n"
          "back peeks are the standard workaround for a peekless deque."),
},
{
 "id": "12.12", "level": "challenge", "title": "Cheapest network (Kruskal)",
 "statement": (
  "Weighted links (w, u, v) can connect n offices. Write kruskal(n, edges): the minimum total\n"
  "cost to connect ALL offices, or None if impossible. Sort edges by weight, take every edge\n"
  "whose union succeeds, stop counting when n-1 merges have landed. sortOn + dsu is the whole\n"
  "algorithm."),
 "contract": "kruskal(n: int, edges: list[tuple]) -> int | None",
 "tests": """>>> kruskal(4, [(1, 0, 1), (2, 1, 2), (10, 0, 2), (3, 2, 3)])
6
>>> kruskal(3, [(5, 0, 1)]) is None
True
>>> kruskal(1, [])
0
>>> kruskal(4, [(4, 0, 1), (1, 2, 3), (2, 1, 2), (7, 0, 3)])
7""",
 "solution": """def kruskal(n, edges):
    f, union = dsu(n)
    total = merges = 0
    for w, u, v in sortOn(fst, edges):
        if union(u, v):
            total += w
            merges += 1
    return total if merges == n - 1 else None""",
 "note": ("Greedy-by-weight is optimal because a cheapest edge crossing any cut belongs to some\n"
          "minimum spanning tree; union==False is the cycle filter. O(E log E) for the sort;\n"
          "the dsu work is effectively linear. merges == n-1 doubles as the connectivity test."),
},
]
