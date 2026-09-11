CHAPTER = 5
TITLE = "The Fold"

ITEMS = [
{
 "id": "5.1", "level": "drill", "title": "Sum of squares",
 "statement": """Using foldl, compute the sum of the squares of a list of integers. The accumulator
carries the running total; seed it with 0 so the empty list answers 0.""",
 "contract": "sum_squares(xs: list[int]) -> int",
 "tests": """>>> sum_squares([1, 2, 3])
14
>>> sum_squares([])
0
>>> sum_squares([-2])
4""",
 "solution": "sum_squares = lambda xs: foldl(lambda acc, x: acc + x * x, xs, 0)",
 "note": "One fold, seed 0, combiner acc + x*x; O(n). Common mistake: squaring the accumulator "
         "instead of the element.",
},
{
 "id": "5.2", "level": "drill", "title": "Longest word, first on ties",
 "statement": """Using foldl1, return the longest word in a non-empty list. When two words tie in
length, the EARLIER one must win -- choose your comparison so the accumulator survives ties.""",
 "contract": "longest_word(ws: list[str]) -> str",
 "tests": """>>> longest_word(["hi", "abc", "de"])
'abc'
>>> longest_word(["aa", "bb"])
'aa'
>>> longest_word(["x"])
'x'""",
 "solution": "longest_word = lambda ws: foldl1(lambda acc, w: w if len(w) > len(acc) else acc, ws)",
 "note": "foldl1 seeds with the first element; the strict > keeps the incumbent on ties. Using >= "
         "would hand ties to the newcomer -- the classic tie-break slip.",
},
{
 "id": "5.3", "level": "drill", "title": "Cons cells by hand",
 "statement": """Using foldr, convert a list into nested pairs ending in None, Lisp-style:
[1, 2, 3] becomes (1, (2, (3, None))). The nesting grows from the right, which is exactly what
foldr does; note its combiner receives (element, accumulator).""",
 "contract": "to_pairs(xs: list) -> tuple | None",
 "tests": """>>> to_pairs([1, 2, 3])
(1, (2, (3, None)))
>>> to_pairs(['a'])
('a', None)
>>> to_pairs([]) is None
True""",
 "solution": "to_pairs = lambda xs: foldr(lambda x, acc: (x, acc), xs, None)",
 "note": "foldr(f, xs, None) with f = make-a-pair; the seed None is the empty-list arm. Trying "
         "this with foldl builds the chain backwards.",
},
{
 "id": "5.4", "level": "drill", "title": "Factorial",
 "statement": """Using product, compute n factorial. Remember product of an empty sequence is 1 --
which is precisely why 0! works with no special case.""",
 "contract": "factorial(n: int) -> int",
 "tests": """>>> factorial(5)
120
>>> factorial(0)
1
>>> factorial(1)
1""",
 "solution": "factorial = lambda n: product(range(1, n + 1))",
 "note": "product is the numeric fold seeded with 1, so the n = 0 case falls out for free; O(n).",
},
{
 "id": "5.5", "level": "drill", "title": "Every substring team name",
 "statement": """Using subsequences, list all subsets of s's characters as strings -- every string
formable by deleting zero or more characters from s (keeping order): powerset_strings("ab") is
['', 'a', 'b', 'ab']. Join each subsequence back into a string; keep subsequences' own order.""",
 "contract": "powerset_strings(s: str) -> list[str]",
 "tests": """>>> powerset_strings("ab")
['', 'a', 'b', 'ab']
>>> powerset_strings("")
['']
>>> len(powerset_strings("abc"))
8""",
 "solution": 'powerset_strings = lambda s: map_("".join, subsequences(s))',
 "note": "subsequences gives lists of characters; one map_ of join finishes. 2^n results -- say "
         "the bound before calling it on anything long.",
},
{
 "id": "5.6", "level": "apply", "title": "Bank statement audit",
 "statement": """A bank account starts at `start` (never negative) and processes a list of signed
transactions in order. Return (final_balance, overdrawn) where overdrawn is True if the running
balance ever dipped below zero at any point -- even if later deposits recovered it. One fold: the
accumulator carries both the balance and the flag.""",
 "contract": "balance_audit(start: int, txns: list[int]) -> tuple[int, bool]",
 "tests": """>>> balance_audit(100, [-150, 75])
(25, True)
>>> balance_audit(100, [])
(100, False)
>>> balance_audit(0, [-1, 1])
(0, True)
>>> balance_audit(10, [5])
(15, False)""",
 "solution": """balance_audit = lambda start, txns: foldl(
    lambda st, x: (st[0] + x, st[1] or st[0] + x < 0), txns, (start, False))""",
 "note": "Tuple accumulator (balance, flag); the `or` latches the flag once tripped. O(n). Common "
         "mistake: checking only the final balance.",
},
{
 "id": "5.7", "level": "apply", "title": "Ways to roll it",
 "statement": """You roll n six-sided dice. Using replicateM, count every way the ordered dice can
sum to exactly target. n is small (n <= 6), so enumerating all 6^n outcomes is the honest play.""",
 "contract": "ways_to_roll(n: int, target: int) -> int",
 "tests": """>>> ways_to_roll(2, 7)
6
>>> ways_to_roll(1, 3)
1
>>> ways_to_roll(2, 13)
0
>>> ways_to_roll(3, 18)
1""",
 "solution": "ways_to_roll = lambda n, target: len([r for r in replicateM(n, range(1, 7)) if sum(r) == "
             "target])",
 "note": "replicateM(n, faces) is every ordered roll; filter and count. 6^n outcomes -- state the "
         "bound. The DP version exists, but at n <= 6 enumeration is simpler and safer.",
},
{
 "id": "5.8", "level": "apply", "title": "Decompress the telemetry",
 "statement": """A sensor stream arrives run-length encoded as (char, count) pairs. Using foldl,
decompress it back into the original string: [('a', 3), ('b', 2)] becomes 'aaabb'.""",
 "contract": "rle_decode(pairs: list[tuple[str, int]]) -> str",
 "tests": """>>> rle_decode([('a', 3), ('b', 2)])
'aaabb'
>>> rle_decode([])
''
>>> rle_decode([('x', 1)])
'x'""",
 "solution": "rle_decode = lambda pairs: foldl(lambda acc, p: acc + p[0] * p[1], pairs, '')",
 "note": "A fold whose accumulator is the output string; char * count expands each run. The "
         "inverse of the g5 rle_encode problem -- round-trip them as a self-check.",
},
{
 "id": "5.9", "level": "apply", "title": "Config templating",
 "statement": """A deployment file is produced by applying find-and-replace edits IN ORDER: each
edit is a (find, replace) pair, and later edits see the result of earlier ones. Using foldl with
the text as the accumulator, apply them all.""",
 "contract": "apply_edits(text: str, edits: list[tuple[str, str]]) -> str",
 "tests": """>>> apply_edits("hello world", [("world", "there"), ("hello", "hi")])
'hi there'
>>> apply_edits("aa", [("a", "b")])
'bb'
>>> apply_edits("cfg:$X", [("$X", "1")])
'cfg:1'
>>> apply_edits("keep", [])
'keep'""",
 "solution": "apply_edits = lambda text, edits: foldl(lambda t, e: t.replace(e[0], e[1]), edits, text)",
 "note": "The accumulator is the evolving TEXT and the list folded over is the edits -- a fold "
         "where state is a document, not a number. Order sensitivity is the point.",
},
{
 "id": "5.10", "level": "apply", "title": "Exact change",
 "statement": """You hold a small pouch of coins, each usable at most once (n <= 20). Using
subsequences, decide whether there is any way to pick a subset of them summing to exactly target.
The empty subset makes 0, so target 0 is always reachable.""",
 "contract": "exact_change(coins: list[int], target: int) -> bool",
 "tests": """>>> exact_change([3, 7, 2], 9)
True
>>> exact_change([5, 10], 7)
False
>>> exact_change([], 0)
True
>>> exact_change([4], 0)
True""",
 "solution": "exact_change = lambda coins, target: any(sum(s) == target for s in subsequences(coins))",
 "note": "The powerset as a brute-force license: 2^n subsets at n <= 20 is about a million cheap "
         "checks. any() stops at the first witness.",
},
{
 "id": "5.11", "level": "challenge", "title": "Minimal hiring committee",
 "statement": """A project needs a set of skills. Each candidate brings a list of skills. Hiring is
expensive, so find the SIZE of the smallest group of candidates that together covers every needed
skill, or -1 if no group can. Candidate count is small (n <= 12): enumerate groups with
subsequences, keep the covering ones, minimise the size. An empty requirement needs zero hires.""",
 "contract": "min_team(required: list[str], candidates: list[list[str]]) -> int",
 "tests": """>>> min_team(["py", "sql"], [["py"], ["sql"], ["py", "sql"]])
1
>>> min_team(["a", "b"], [["a"], ["b"]])
2
>>> min_team(["go"], [["py"]])
-1
>>> min_team([], [["x"]])
0""",
 "solution": """def min_team(required, candidates):
    covers = [s for s in subsequences(candidates) if set(required) <= set(concat(s))]
    return min(map_(len, covers), default=-1)""",
 "note": "Set cover is NP-hard in general; n <= 12 licenses the 2^n sweep. concat flattens a "
         "group's skills; set inclusion checks coverage; min with default handles impossibility.",
},
{
 "id": "5.12", "level": "challenge", "title": "Fair loot split",
 "statement": """Two players split a pile of treasure items (values, n <= 20) into two groups; every
item goes to one side. Return the smallest possible absolute difference between the two groups'
totals. Observe that choosing one side's subset s fixes the difference to abs(total - 2*sum(s)),
then let subsequences try every side.""",
 "contract": "min_partition_diff(xs: list[int]) -> int",
 "tests": """>>> min_partition_diff([1, 6, 11, 5])
1
>>> min_partition_diff([3, 1])
2
>>> min_partition_diff([2, 2])
0
>>> min_partition_diff([])
0
>>> min_partition_diff([7])
7""",
 "solution": """def min_partition_diff(xs):
    total = sum(xs)
    return min(abs(total - 2 * sum(s)) for s in subsequences(xs))""",
 "note": "The classic balanced-partition interview problem, honestly brute-forced: one algebraic "
         "observation turns it into a powerset minimum. 2^n at n <= 20; the DP version is the "
         "follow-up conversation.",
},
{
 "id": "5.13", "level": "challenge", "title": "Next greater reading",
 "statement": """Daily sensor readings arrive as a list. For each position report the NEXT GREATER
reading to its right -- the first later value strictly larger -- or -1 when no later reading beats
it. A double loop is O(n^2); a list used as a stack of still-unanswered positions, driven by one
left-to-right fold, answers everything in O(n).""",
 "contract": "next_greater(xs: list[int]) -> list[int]",
 "tests": """>>> next_greater([2, 1, 3])
[3, 3, -1]
>>> next_greater([1, 2, 3, 4])
[2, 3, 4, -1]
>>> next_greater([4, 3, 2, 1])
[-1, -1, -1, -1]
>>> next_greater([2, 2])
[-1, -1]
>>> next_greater([])
[]""",
 "solution": """def next_greater(xs):
    res = [-1] * len(xs)
    def step(stack, i):
        while stack and xs[stack[-1]] < xs[i]:
            res[stack.pop()] = xs[i]
        stack.append(i)
        return stack
    foldl(step, range(len(xs)), [])
    return res""",
 "note": "The monotonic stack holds indices still waiting for their answer; each index is pushed "
         "once and popped at most once, so the fold is O(n). 'Next greater' is the recognition "
         "ladder's textbook STACK trigger -- same skeleton as matching pairs of brackets.",
},
]
