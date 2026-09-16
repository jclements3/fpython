CHAPTER = 6
TITLE = "Scans"

ITEMS = [
{
 "id": "6.1", "level": "drill", "title": "Running maximum",
 "statement": """Using scanl1, produce the running maximum of a list: element i of the answer is the
largest value seen among the first i+1 inputs. An empty list yields an empty scan.""",
 "contract": "running_max(xs: list[int]) -> list[int]",
 "tests": """>>> running_max([3, 1, 4, 1, 5])
[3, 3, 4, 4, 5]
>>> running_max([7])
[7]
>>> running_max([])
[]""",
 "solution": "running_max = lambda xs: scanl1(max, xs)",
 "note": "scanl1 seeds with the first element and keeps every intermediate; max is the combiner. "
         "O(n). This scan IS the best-so-far column of many DP tables.",
},
{
 "id": "6.2", "level": "drill", "title": "Account history",
 "statement": """An account opens at balance `start` and applies signed transactions in order. Using
scanl, return the FULL balance history -- the balance at each step, opening balance first --
len(txns) + 1 entries.""",
 "contract": "account_history(start: int, txns: list[int]) -> list[int]",
 "tests": """>>> account_history(100, [-20, 50])
[100, 80, 130]
>>> account_history(0, [])
[0]
>>> account_history(5, [-10])
[5, -5]""",
 "solution": "account_history = lambda start, txns: scanl(add, start, txns)",
 "note": "scanl's seed appears as the first output, which models the opening balance exactly; the "
         "n+1 length is the contract, not a bug.",
},
{
 "id": "6.3", "level": "drill", "title": "Suffix sums",
 "statement": """Using scanr, compute suffix sums: element i is the sum of xs[i:], and the final
element is the seed 0 (the empty suffix). [1, 2, 3] becomes [6, 5, 3, 0].""",
 "contract": "suffix_sums(xs: list[int]) -> list[int]",
 "tests": """>>> suffix_sums([1, 2, 3])
[6, 5, 3, 0]
>>> suffix_sums([])
[0]
>>> suffix_sums([5])
[5, 0]""",
 "solution": "suffix_sums = lambda xs: scanr(add, 0, xs)",
 "note": "scanr folds from the right and keeps every suffix's result; the whole-list answer lands "
         "first. Mirror image of prefix sums.",
},
{
 "id": "6.4", "level": "drill", "title": "Best price still ahead",
 "statement": """Shopping day: prices[i] is today's price at shop i, and you may only buy at the
CURRENT shop or a later one. Using scanr1, compute for each position the cheapest price from there
to the end of the street.""",
 "contract": "best_remaining(prices: list[int]) -> list[int]",
 "tests": """>>> best_remaining([5, 3, 8, 2, 4])
[2, 2, 2, 2, 4]
>>> best_remaining([7])
[7]
>>> best_remaining([4, 6])
[4, 6]""",
 "solution": "best_remaining = lambda prices: scanr1(min, prices)",
 "note": "A right-to-left running minimum: scanr1(min). Pairing it with a left scan is the shape "
         "of many buy/sell problems.",
},
{
 "id": "6.5", "level": "drill", "title": "Running product",
 "statement": """Using accumulate with a custom combiner, produce the running product of a list:
[2, 3, 4] becomes [2, 6, 24]. Remember accumulate is a generator -- deliver a list.""",
 "contract": "running_product(xs: list[int]) -> list[int]",
 "tests": """>>> running_product([2, 3, 4])
[2, 6, 24]
>>> running_product([])
[]
>>> running_product([5])
[5]""",
 "solution": "running_product = lambda xs: list(accumulate(xs, lambda a, b: a * b))",
 "note": "accumulate defaults to addition; hand it * for products. It yields lazily, so list() "
         "materialises -- forgetting that is the usual slip.",
},
{
 "id": "6.6", "level": "apply", "title": "Record-breaking days",
 "statement": """A weather station logs one temperature per day. A day sets a RECORD if it is
strictly hotter than every previous day; the first day always counts. Count the record days.
Hint: on the running-maximum scan, records are exactly where consecutive entries strictly rise --
pairwise makes those visible.""",
 "contract": "new_records(temps: list[int]) -> int",
 "tests": """>>> new_records([3, 1, 4, 4, 5])
3
>>> new_records([2, 2, 2])
1
>>> new_records([1, 2, 3])
3
>>> new_records([])
0""",
 "solution": """def new_records(temps):
    if temps == []:
        return 0
    return 1 + len([1 for a, b in pairwise(scanl1(max, temps)) if b > a])""",
 "note": "scanl1(max) turns history into a staircase; each strict step up is a record, plus one "
         "for day zero. Watch the tie case: equalling the record is not breaking it.",
},
{
 "id": "6.7", "level": "apply", "title": "Range-sum service",
 "statement": """A dashboard must answer many sum queries over the same fixed list: each query
(i, j) asks for the sum of xs[i:j]. Precompute prefix sums ONCE with scanl, then answer every
query in O(1) as pre[j] - pre[i].""",
 "contract": "range_sums(xs: list[int], queries: list[tuple[int, int]]) -> list[int]",
 "tests": """>>> range_sums([3, 1, 4, 1], [(0, 2), (1, 3)])
[4, 5]
>>> range_sums([2, 2, 2], [(0, 3)])
[6]
>>> range_sums([1, 2], [])
[]
>>> range_sums([5], [(0, 0)])
[0]""",
 "solution": """def range_sums(xs, queries):
    pre = scanl(add, 0, xs)
    return map_(lambda q: pre[q[1]] - pre[q[0]], queries)""",
 "note": "One O(n) scan converts every window question into two array reads. The seed 0 makes "
         "pre[i] the sum of the first i elements, so half-open (i, j) needs no off-by-one fixups.",
},
{
 "id": "6.8", "level": "apply", "title": "Fuel gauge report",
 "statement": """A rover starts with `start` units of fuel and applies signed fuel deltas (burns and
top-ups) in order. Report (lowest_level_ever, mission_ok) where mission_ok means the level --
including the starting level -- never went negative. Scan the history once, then read both answers
off it.""",
 "contract": "fuel_report(start: int, deltas: list[int]) -> tuple[int, bool]",
 "tests": """>>> fuel_report(10, [-4, -5, 3, -6])
(-2, False)
>>> fuel_report(5, [-1])
(4, True)
>>> fuel_report(0, [])
(0, True)""",
 "solution": """def fuel_report(start, deltas):
    history = scanl(add, start, deltas)
    return (min(history), min(history) >= 0)""",
 "note": "The scan is the whole flight recorder; min answers both questions. A bare fold would "
         "need a compound accumulator to remember the low-water mark.",
},
{
 "id": "6.9", "level": "apply", "title": "Maximum drawdown",
 "statement": """Risk teams measure a stock's worst fall from a prior peak: the maximum of
peak_so_far - price over all days. Compute it by zipping the running maximum against the prices
themselves; a never-falling series has drawdown 0.""",
 "contract": "drawdown(prices: list[int]) -> int",
 "tests": """>>> drawdown([5, 3, 8, 4, 7])
4
>>> drawdown([1, 2, 3])
0
>>> drawdown([10])
0
>>> drawdown([])
0""",
 "solution": """def drawdown(prices):
    if prices == []:
        return 0
    return max(zipWith(lambda peak, p: peak - p, scanl1(max, prices), prices))""",
 "note": "scanl1(max) is the peak line; zipWith subtracts the actual price under it. The mirror "
         "of best-time-to-sell: there you chase rises off the running MIN.",
},
{
 "id": "6.10", "level": "apply", "title": "Peak concurrency",
 "statement": """Sessions occupy overlapping intervals of time; the log records them as +1 for each
opening and -1 for each closing, in time order. Report the highest number of simultaneously open
sessions; with no events the answer is 0. Scan the deltas from 0 and take the highest point.""",
 "contract": "peak_concurrency(events: list[int]) -> int",
 "tests": """>>> peak_concurrency([1, 1, -1, 1, -1])
2
>>> peak_concurrency([1, -1, 1, -1])
1
>>> peak_concurrency([])
0""",
 "solution": "peak_concurrency = lambda events: max(scanl(add, 0, events))",
 "note": "The seed 0 doubles as the empty-log answer since scanl always emits it. This is the "
         "sweep-line pattern in miniature: deltas, running level, extremum.",
},
{
 "id": "6.11", "level": "challenge", "title": "Trapped rainwater",
 "statement": """After a storm, water sits on a skyline of bar heights: above each bar, water fills
up to the LOWER of the tallest bar to its left and the tallest to its right (itself included),
minus the bar's own height. Total the trapped water. Two scans -- a running max from the left and
one from the right -- plus one zipWith3 finish it in O(n). The classic interview problem, solved
the scan way.""",
 "contract": "trapped(heights: list[int]) -> int",
 "tests": """>>> trapped([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
6
>>> trapped([2, 0, 2])
2
>>> trapped([1, 2, 3])
0
>>> trapped([])
0""",
 "solution": """def trapped(heights):
    if heights == []:
        return 0
    lmax, rmax = scanl1(max, heights), scanr1(max, heights)
    return sum(zipWith3(lambda l, r, h: min(l, r) - h, lmax, rmax, heights))""",
 "note": "LeetCode 42 without a single index: left-max scan, right-max scan, pointwise "
         "min(l, r) - h. Each term is >= 0 because each scan includes the bar itself.",
},
{
 "id": "6.12", "level": "challenge", "title": "Best sightseeing pair",
 "statement": """A road trip visits spots with scores. Choosing spots i < j earns
score[i] + score[j] + i - j (distance decays the fun). Maximise over all pairs, in O(n): note the
formula splits into (score[i] + i) + (score[j] - j), so a running maximum of the first part, one
step behind, meets each j. At least two spots are guaranteed.""",
 "contract": "best_pair(scores: list[int]) -> int",
 "tests": """>>> best_pair([8, 1, 5, 2, 6])
11
>>> best_pair([1, 2])
2
>>> best_pair([1, 1, 1])
1""",
 "solution": """def best_pair(scores):
    gain = scanl1(max, map_(lambda p: p[1] + p[0], enum(scores)))
    drop = map_(lambda p: p[1] - p[0], enum(scores))
    return max(zipWith(lambda g, d: g + d, init(gain), tail(drop)))""",
 "note": "LeetCode 1014: split the pair formula, scan the left part's running max, zip it one "
         "position behind the right part. init/tail do the i < j offset with no index fiddling.",
},
]
