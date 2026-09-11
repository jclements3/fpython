"""Homework bank -- Chapter 10: Dict Folds and Bags."""

CHAPTER = 10
TITLE = "Dict Folds and Bags"

ITEMS = [
{
 "id": "10.1", "level": "drill", "title": "Vowel census",
 "statement": """Count the frequency of each vowel (a, e, i, o, u) in a string, case-insensitive.
Return the counts as (vowel, count) pairs sorted alphabetically; vowels that never occur are
omitted.""",
 "contract": "vowel_census(s: str) -> list[tuple[str, int]]",
 "tests": """>>> vowel_census("Banana")
[('a', 3)]
>>> vowel_census("queue")
[('e', 2), ('u', 2)]
>>> vowel_census("xyz")
[]""",
 "solution": ("vowel_census = lambda s: sorted(\n"
              '    Counter(filter_(lambda ch: ch in "aeiou", s.lower())).items())'),
 "note": "filter_ narrows to vowels, Counter folds the counts, sorted makes the "
         "output deterministic. Reading Counter with [] would autovivify zeros -- "
         "returning .items() sidesteps that entirely.",
},
{
 "id": "10.2", "level": "drill", "title": "Order totals",
 "statement": """An order log is a list of (product, quantity) pairs; products repeat. Total the
quantity per product with one fromListWith fold. Keys keep first-seen order.""",
 "contract": "totals(pairs: list[tuple[str, int]]) -> dict[str, int]",
 "tests": """>>> totals([("apple", 2), ("pear", 1), ("apple", 3)])
{'apple': 5, 'pear': 1}
>>> totals([])
{}
>>> totals([("kiwi", 4)])
{'kiwi': 4}""",
 "solution": "totals = lambda pairs: fromListWith(lambda new, old: new + old, pairs)",
 "note": "Addition is commutative, so the f(new, old) order cannot bite here. "
         "This is THE dict-building fold at its simplest: pairs in, totals out, O(n).",
},
{
 "id": "10.3", "level": "drill", "title": "Longest run",
 "statement": """Return the length of the longest run of consecutive equal characters in a string
(0 for the empty string). group hands you the runs; you measure them.""",
 "contract": "longest_run(s: str) -> int",
 "tests": """>>> longest_run("aaabb")
3
>>> longest_run("abab")
1
>>> longest_run("")
0""",
 "solution": "longest_run = lambda s: max(map_(len, group(s)), default=0)",
 "note": "group returns bare runs ([[a]]), so map_ len measures them directly; "
         "default=0 covers the empty string. One pass, O(n).",
},
{
 "id": "10.4", "level": "drill", "title": "Restock, persistently",
 "statement": """Given a warehouse inventory dict and one delivery (item, quantity), return a NEW
inventory with the delivery added to that item's count -- and leave the original dict untouched,
which is exactly insertWith's contract. New items simply appear.""",
 "contract": "restock(inv: dict[str, int], item: str, qty: int) -> dict[str, int]",
 "tests": """>>> inv = {'nail': 10}
>>> restock(inv, 'nail', 5)
{'nail': 15}
>>> inv
{'nail': 10}
>>> restock(inv, 'screw', 3)
{'nail': 10, 'screw': 3}""",
 "solution": "restock = lambda inv, item, qty: insertWith(lambda new, old: new + old, item, qty, inv)",
 "note": "insertWith copies the dict first -- that copy IS the persistence -- then "
         "combines f(new, old) on collision. Mutating inv directly is the mistake "
         "this drill exists to catch.",
},
{
 "id": "10.5", "level": "drill", "title": "Tile check",
 "statement": """Scrabble-style: can a word be assembled from a hand of letter tiles, respecting
multiplicity (two o's in the word need two o tiles)? This is multiset inclusion -- one bag_sub.""",
 "contract": "can_build(word: str, tiles: str) -> bool",
 "tests": """>>> can_build("cat", "tacos")
True
>>> can_build("book", "bok")
False
>>> can_build("", "xyz")
True""",
 "solution": "can_build = lambda word, tiles: bag_sub(Counter(word), Counter(tiles))",
 "note": "Two Counter folds and an inclusion test; O(n + m). A set-based check is "
         "the classic wrong answer -- it ignores multiplicity.",
},
{
 "id": "10.6", "level": "apply", "title": "High-water marks",
 "statement": """Two flood sensors each report per-zone water maxima as a dict. Combine them into
one report keeping the HIGHER reading for zones both saw; zones only one sensor saw pass through
unchanged. Choose the right combining function for unionWith -- the monoid is the design decision.""",
 "contract": "high_water(a: dict[str, int], b: dict[str, int]) -> dict[str, int]",
 "tests": """>>> high_water({'north': 3, 'south': 7}, {'south': 9, 'east': 2})
{'north': 3, 'south': 9, 'east': 2}
>>> high_water({}, {'west': 1})
{'west': 1}
>>> high_water({'north': 4}, {})
{'north': 4}""",
 "solution": "high_water = lambda a, b: unionWith(max, a, b)",
 "note": "unionWith(max) is exactly bag_union generalized to any dict; a's keys keep "
         "their positions, b's new keys append. Swapping in addition would instead "
         "give a summing merge -- same shape, different monoid.",
},
{
 "id": "10.7", "level": "apply", "title": "Click sessions",
 "statement": """A user's click timestamps arrive sorted. Clicks belong to one session while they
fall within 30 seconds OF THE SESSION'S FIRST CLICK; a later click starts a new session. Split the
timestamps into sessions -- note this is groupBy's compare-against-the-run's-FIRST semantics,
verbatim, not a neighbor-gap rule.""",
 "contract": "sessions(ts: list[int]) -> list[list[int]]",
 "tests": """>>> sessions([0, 10, 25, 50, 60, 100])
[[0, 10, 25], [50, 60], [100]]
>>> sessions([])
[]
>>> sessions([5])
[[5]]""",
 "solution": "sessions = lambda ts: groupBy(lambda start, t: t - start <= 30, ts)",
 "note": "groupBy hands eq the run's FIRST element and each newcomer -- precisely "
         "the anchored-window rule. A neighbor-gap rule would need pairwise instead; "
         "confusing the two is the point of this exercise.",
},
{
 "id": "10.8", "level": "apply", "title": "Department roster",
 "statement": """HR exports (department, employee) rows in hiring order. Build a dict mapping each
department to its employees IN HIRING ORDER. Mind fromListWith's f(new, old) argument order: a
bare concat would reverse each roster.""",
 "contract": "roster(rows: list[tuple[str, str]]) -> dict[str, list[str]]",
 "tests": """>>> roster([("eng", "ann"), ("ops", "bob"), ("eng", "cy")])
{'eng': ['ann', 'cy'], 'ops': ['bob']}
>>> roster([])
{}
>>> roster([("qa", "dee")])
{'qa': ['dee']}""",
 "solution": ("roster = lambda rows: fromListWith(\n"
              "    lambda new, old: old + new, [(d, [e]) for d, e in rows])"),
 "note": "Wrap each employee as a one-element list, then combine old + new to keep "
         "arrival order -- f receives the NEW value first (Haskell's order), so a "
         "plain (+) reverses every roster. That reversal is the classic gotcha.",
},
{
 "id": "10.9", "level": "apply", "title": "Shopping list",
 "statement": """A recipe lists its ingredients with repeats ('egg' twice means two eggs); your
pantry is a list of what you have. Produce the shopping list -- what is still missing and how many
of each -- as (item, count) pairs sorted alphabetically. Multiset difference, clipped at zero.""",
 "contract": "shopping_list(need: list[str], have: list[str]) -> list[tuple[str, int]]",
 "tests": """>>> shopping_list(["egg", "egg", "milk"], ["egg"])
[('egg', 1), ('milk', 1)]
>>> shopping_list(["jam"], ["jam", "jam"])
[]
>>> shopping_list([], ["salt"])
[]""",
 "solution": ("shopping_list = lambda need, have: sorted(\n"
              "    bag_diff(Counter(need), Counter(have)).items())"),
 "note": "bag_diff subtracts with clipping at zero, so surplus pantry items vanish "
         "rather than going negative; sorted makes the output order deterministic.",
},
{
 "id": "10.10", "level": "apply", "title": "Traffic rollup",
 "statement": """Each server in a fleet reports a dict of per-page visit counts. Roll the whole
fleet up into one dict of grand totals. This is a FOLD whose combining step is itself a unionWith
-- dict-merging as a monoid.""",
 "contract": "rollup(reports: list[dict[str, int]]) -> dict[str, int]",
 "tests": """>>> rollup([{'home': 1}, {'home': 2, 'faq': 5}, {'faq': 1}])
{'home': 3, 'faq': 6}
>>> rollup([])
{}
>>> rollup([{'a': 1}])
{'a': 1}""",
 "solution": ("rollup = lambda reports: foldl(\n"
              "    lambda acc, d: unionWith(lambda x, y: x + y, acc, d), reports, {})"),
 "note": "unionWith(+) merges two reports; foldl extends that to any number, seeded "
         "with the empty dict (the monoid's identity). Key order: first server to "
         "mention a page owns its position.",
},
{
 "id": "10.11", "level": "challenge", "title": "Majority element",
 "statement": """An election log is a list of votes. The most common candidate wins only with a
STRICT majority (more than half of all votes): return that candidate, or None when nobody
qualifies. Ties for the top count must not invent a majority. Count with a bag; interrogate it
deterministically.""",
 "contract": "majority(xs: list) -> value | None",
 "tests": """>>> majority([1, 2, 1, 1])
1
>>> majority([1, 2]) is None
True
>>> majority([]) is None
True
>>> majority([5])
5""",
 "solution": ("def majority(xs):\n"
              "    if not xs:\n"
              "        return None\n"
              "    c = Counter(xs)\n"
              "    best = maxOn(lambda k: c[k], sorted(c))\n"
              "    return best if c[best] * 2 > len(xs) else None"),
 "note": "Counter tallies in O(n); maxOn over the sorted keys picks a deterministic "
         "top; the strict > len/2 test rejects mere pluralities. Interview "
         "escalation: Boyer-Moore voting does it in O(1) space -- name it.",
},
{
 "id": "10.12", "level": "challenge", "title": "Top spender per city",
 "statement": """A payment feed yields (city, customer, amount) rows; customers repeat. For every
city, find the customer with the highest TOTAL spend there; break ties by taking the
alphabetically first name. Return {city: customer} with cities in first-appearance order. Two
stacked dict folds: totals per (city, customer), then a per-city best.""",
 "contract": "top_spender(rows: list[tuple[str, str, int]]) -> dict[str, str]",
 "tests": """>>> top_spender([("nyc", "ann", 50), ("nyc", "bob", 70), ("la", "cy", 20),
...              ("nyc", "ann", 30)])
{'nyc': 'ann', 'la': 'cy'}
>>> top_spender([("sf", "a", 10), ("sf", "b", 10)])
{'sf': 'a'}
>>> top_spender([])
{}""",
 "solution": ("def top_spender(rows):\n"
              "    totals = fromListWith(lambda n, o: n + o, [((c, p), a) for c, p, a in rows])\n"
              "    per_city = fromListWith(lambda n, o: o + n,\n"
              "                            [(c, [(p, t)]) for (c, p), t in totals.items()])\n"
              "    return {c: minOn(lambda pt: (-pt[1], pt[0]), ps)[0] for c, ps in per_city.items()}"),
 "note": "Fold one: totals keyed by the (city, customer) PAIR. Fold two: regroup by "
         "city, keeping arrival order with old + new. minOn over (-total, name) gets "
         "highest-spend-then-alphabetical in one key. O(n) folds plus a per-city scan.",
},
]
