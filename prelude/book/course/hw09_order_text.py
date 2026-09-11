"""Homework bank -- Chapter 9: Order and Text."""

CHAPTER = 9
TITLE = "Order and Text"

ITEMS = [
{
 "id": "9.1", "level": "drill", "title": "Sort by size, then spelling",
 "statement": """Sort a list of words shortest-first; words of equal length appear in alphabetical
order. One sortOn with a tuple key does both levels at once.""",
 "contract": "sort_by_size(ws: list[str]) -> list[str]",
 "tests": """>>> sort_by_size(["bb", "a", "ccc", "aa"])
['a', 'aa', 'bb', 'ccc']
>>> sort_by_size(["same", "size", "abcd"])
['abcd', 'same', 'size']
>>> sort_by_size([])
[]""",
 "solution": "sort_by_size = lambda ws: sortOn(lambda w: (len(w), w), ws)",
 "note": "Tuple keys sort level by level; O(n log n). Common mistake: two separate "
         "sorts, which works only because Python's sort is stable but hides the intent.",
},
{
 "id": "9.2", "level": "drill", "title": "Closest to zero",
 "statement": """Return the element of a non-empty list closest to zero. If two elements tie in
distance (like -2 and 2), the one appearing FIRST in the list wins.""",
 "contract": "closest_to_zero(xs: list[int]) -> int",
 "tests": """>>> closest_to_zero([3, -1, 4])
-1
>>> closest_to_zero([-2, 2])
-2
>>> closest_to_zero([7])
7""",
 "solution": "closest_to_zero = lambda xs: minOn(abs, xs)",
 "note": "minOn is O(n) and keeps the first winner on ties -- no sort needed. "
         "Sorting first would cost O(n log n) and lose the arrival tie-break.",
},
{
 "id": "9.3", "level": "drill", "title": "Count occurrences in sorted data",
 "statement": """Given an ALREADY-SORTED list and a value, count how many times the value occurs --
in O(log n), using the two bisects. No scanning allowed.""",
 "contract": "count_val(sorted_xs: list[int], x: int) -> int",
 "tests": """>>> count_val([1, 2, 2, 2, 3], 2)
3
>>> count_val([1, 3], 2)
0
>>> count_val([], 5)
0""",
 "solution": "count_val = lambda xs, x: bisect_right(xs, x) - bisect_left(xs, x)",
 "note": "bisect_left finds the first slot >= x, bisect_right the first > x; the gap "
         "between them IS the run of equals. Two O(log n) probes, zero scanning.",
},
{
 "id": "9.4", "level": "drill", "title": "Normalize spacing",
 "statement": """Collapse any runs of whitespace in a sentence to single spaces and strip the ends,
using the words/unwords round trip.""",
 "contract": "normalize_spaces(s: str) -> str",
 "tests": """>>> normalize_spaces("  such   spacing  ")
'such spacing'
>>> normalize_spaces("one")
'one'
>>> normalize_spaces("")
''""",
 "solution": "normalize_spaces = lambda s: unwords(words(s))",
 "note": "words splits on any whitespace runs; unwords rejoins with single spaces. "
         "The round trip IS the normalizer -- no regex required.",
},
{
 "id": "9.5", "level": "drill", "title": "Three-way merge",
 "statement": """Merge three already-sorted lists into one sorted list by chaining the two-list
merge. Stability must hold: on equal values, earlier-argument elements come first.""",
 "contract": "merge3(a: list, b: list, c: list) -> list",
 "tests": """>>> merge3([1, 4], [2, 5], [3, 6])
[1, 2, 3, 4, 5, 6]
>>> merge3([], [7], [])
[7]
>>> merge3([1, 1], [1], [0])
[0, 1, 1, 1]""",
 "solution": "merge3 = lambda a, b, c: merge(merge(a, b), c)",
 "note": "merge is associative, so nesting two calls gives a three-way merge in "
         "O(n) total. This chaining is the seed of k-way merging.",
},
{
 "id": "9.6", "level": "apply", "title": "Tournament leaderboard",
 "statement": """A tournament reports (name, score) pairs. Produce the leaderboard: names only,
highest score first, and players with equal scores listed alphabetically. One key, two levels.""",
 "contract": "leaderboard(entries: list[tuple[str, int]]) -> list[str]",
 "tests": """>>> leaderboard([("ann", 50), ("bob", 70), ("cy", 50)])
['bob', 'ann', 'cy']
>>> leaderboard([("zed", 10)])
['zed']
>>> leaderboard([])
[]""",
 "solution": "leaderboard = lambda es: map_(fst, sortOn(lambda e: (-e[1], e[0]), es))",
 "note": "The (-score, name) tuple key gets descending score and ascending name in "
         "one sort; reverse=True could not, since it would flip the names too.",
},
{
 "id": "9.7", "level": "apply", "title": "Shipping classes",
 "statement": """Parcels are classed by weight with cutoffs at 1, 5 and 20 kilograms: under 1 is an
'envelope', then 'small', then 'medium', and 20 or over is 'freight' -- a parcel exactly at a
cutoff belongs to the higher class. Replace the if/elif ladder with one bisect over the cutoffs.""",
 "contract": "shipping_class(w: float) -> str",
 "tests": """>>> shipping_class(0.5)
'envelope'
>>> shipping_class(1)
'small'
>>> shipping_class(4.9)
'small'
>>> shipping_class(20)
'freight'""",
 "solution": ("shipping_class = lambda w: "
              '["envelope", "small", "medium", "freight"][bisect_right([1, 5, 20], w)]'),
 "note": "Every threshold ladder is a sorted list in disguise; bisect_right sends "
         "boundary values upward. Mistake to know: bisect_left would send them down.",
},
{
 "id": "9.8", "level": "apply", "title": "Version sort",
 "statement": """Sort dotted version strings like '1.10' and '1.2' in true numeric order (so '1.2'
precedes '1.10'). Shorter versions that are a prefix of longer ones come first.""",
 "contract": "sort_versions(vs: list[str]) -> list[str]",
 "tests": """>>> sort_versions(["1.10", "1.2", "2.0"])
['1.2', '1.10', '2.0']
>>> sort_versions(["0.9", "0.10.1", "0.10"])
['0.9', '0.10', '0.10.1']
>>> sort_versions(["3"])
['3']""",
 "solution": 'sort_versions = lambda vs: sortOn(lambda v: [int(p) for p in v.split(".")], vs)',
 "note": "The key turns each version into a list of ints, and Python compares lists "
         "elementwise with shorter-prefix-first -- exactly version semantics. Sorting "
         "the raw strings is the classic bug ('1.10' < '1.2' lexically).",
},
{
 "id": "9.9", "level": "apply", "title": "Sort the score report",
 "statement": """A report arrives as newline-separated lines of 'name score'. Return the same
report with lines ordered by score descending, ties broken by name ascending -- rebuilt with
unlines, so the result ends with a newline.""",
 "contract": "sort_report(text: str) -> str",
 "tests": """>>> sort_report("ann 50\\nbob 70")
'bob 70\\nann 50\\n'
>>> sort_report("cy 70\\nbob 70\\nann 50")
'bob 70\\ncy 70\\nann 50\\n'
>>> sort_report("solo 1")
'solo 1\\n'""",
 "solution": ("sort_report = lambda text: unlines(\n"
              "    sortOn(lambda l: (-int(words(l)[1]), words(l)[0]), lines(text)))"),
 "note": "lines/unlines bracket the pipeline; the tuple key does both orderings. "
         "unlines terminates every line, hence the trailing newline in the contract.",
},
{
 "id": "9.10", "level": "apply", "title": "Combined guest list",
 "statement": """Two venues export their guest ids as sorted lists which may share entries. Produce
one sorted list with each id appearing once. Merge first, then deduplicate -- both passes linear.""",
 "contract": "merge_unique(a: list[int], b: list[int]) -> list[int]",
 "tests": """>>> merge_unique([1, 3, 5], [1, 2, 5])
[1, 2, 3, 5]
>>> merge_unique([], [4, 4])
[4]
>>> merge_unique([2], [])
[2]""",
 "solution": "merge_unique = lambda a, b: nub(merge(a, b))",
 "note": "merge keeps the result sorted in O(n+m); nub then removes adjacent (and "
         "any) duplicates keeping first occurrences. Sorting a concatenation would "
         "also work but pays O(n log n) for order the inputs already had.",
},
{
 "id": "9.11", "level": "challenge", "title": "Median of two sorted lists",
 "statement": """Two sensors deliver their readings as sorted lists. Return the median of ALL
readings as a float: the middle element of the combined order, or the mean of the two middles when
the total count is even. At least one reading is guaranteed. A linear merge is accepted here; name
the O(log(n+m)) partition approach in your complexity remarks.""",
 "contract": "median_sorted(a: list[int], b: list[int]) -> float",
 "tests": """>>> median_sorted([1, 3], [2])
2.0
>>> median_sorted([1, 2], [3, 4])
2.5
>>> median_sorted([], [5])
5.0
>>> median_sorted([1, 1], [1])
1.0""",
 "solution": ("def median_sorted(a, b):\n"
              "    m = merge(a, b)\n"
              "    n = len(m)\n"
              "    return float(m[n // 2]) if n % 2 else (m[n // 2 - 1] + m[n // 2]) / 2"),
 "note": "merge gives the combined order in O(n+m); the median reads off the middle. "
         "The famous interview escalation is the O(log) binary-partition version -- "
         "know that it exists and say so.",
},
{
 "id": "9.12", "level": "challenge", "title": "Longest common prefix",
 "statement": """Return the longest prefix shared by EVERY string in a list (empty string when the
list is empty or shares nothing). Insight to find: after sorting, only the FIRST and LAST strings
need comparing -- anything they share, every string between them shares too.""",
 "contract": "common_prefix(ws: list[str]) -> str",
 "tests": """>>> common_prefix(["flower", "flow", "flight"])
'fl'
>>> common_prefix(["dog", "cat"])
''
>>> common_prefix([])
''
>>> common_prefix(["same"])
'same'""",
 "solution": ("def common_prefix(ws):\n"
              "    if not ws:\n"
              '        return ""\n'
              "    ss = sorted(ws)\n"
              "    keep = takeWhile(lambda p: p[0] == p[1], zip_(ss[0], ss[-1]))\n"
              '    return "".join(map_(fst, keep))'),
 "note": "Sorting makes the lexicographic extremes the only witnesses needed; "
         "zip_ + takeWhile walks the agreement. O(S log n) for total char count S. "
         "Common mistake: comparing only adjacent pairs and merging results.",
},
]
