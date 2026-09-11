CHAPTER = 4
TITLE = "Lists II: Higher-Order"

ITEMS = [
    # ---------------------------------------------------------------- drills
    {
        "id": "4.1",
        "level": "drill",
        "title": "Squares of the evens",
        "statement": (
            "Given a list of integers, return the squares of just the even ones, in order. This is\n"
            "the filter-then-map pipeline in its smallest form."
        ),
        "contract": "squares_of_evens(xs: list) -> list",
        "tests": """
>>> squares_of_evens([1, 2, 3, 4])
[4, 16]
>>> squares_of_evens([1, 3, 5])
[]
>>> squares_of_evens([])
[]
""",
        "solution": "squares_of_evens = lambda xs: map_(lambda x: x * x, filter_(even, xs))",
        "note": (
            "filter_ selects, map_ transforms -- read the pipeline inside-out, filter first. O(n). "
            "even is the prelude predicate, ready to hand to filter_."
        ),
    },
    {
        "id": "4.2",
        "level": "drill",
        "title": "First over the line",
        "statement": (
            "Return the first element of a list strictly greater than a threshold, or None if no\n"
            "element qualifies. Stop at the first hit -- do not scan the whole list."
        ),
        "contract": "first_over(xs: list, t) -> value | None",
        "tests": """
>>> first_over([1, 5, 3, 9], 4)
5
>>> first_over([1, 2, 3], 9) is None
True
>>> first_over([], 0) is None
True
""",
        "solution": "first_over = lambda xs, t: find(lambda x: x > t, xs)",
        "note": (
            "find is the early exit a fold cannot make: it produces elements lazily and stops at "
            "the first match, returning None on failure. O(k) where k is the winner's position."
        ),
    },
    {
        "id": "4.3",
        "level": "drill",
        "title": "Pass / fail split",
        "statement": (
            "Split exam scores into (passed, failed) against a cutoff, where a score >= cutoff\n"
            "passes. Keep both groups in their original order and make a single pass."
        ),
        "contract": "split_pass_fail(scores: list, cutoff: int) -> tuple",
        "tests": """
>>> split_pass_fail([50, 80, 60, 90], 70)
([80, 90], [50, 60])
>>> split_pass_fail([], 70)
([], [])
>>> split_pass_fail([100, 100], 50)
([100, 100], [])
""",
        "solution": "split_pass_fail = lambda scores, cutoff: partition(lambda s: s >= cutoff, scores)",
        "note": (
            "partition returns (keepers, rest) in one pass, calling the predicate exactly once per "
            "element -- cheaper and clearer than two filter_ passes. O(n)."
        ),
    },
    {
        "id": "4.4",
        "level": "drill",
        "title": "Salvage the integers",
        "statement": (
            "Given a list of string tokens, return the integers among them, in order, dropping any\n"
            "token that is not a (possibly negative) integer. Empty strings are dropped."
        ),
        "contract": "clean_ints(tokens: list) -> list",
        "tests": """
>>> clean_ints(["12", "x", "-3", ""])
[12, -3]
>>> clean_ints(["0", "00"])
[0, 0]
>>> clean_ints(["nope"])
[]
""",
        "solution": (
            'clean_ints = lambda toks: mapMaybe(\n'
            '    lambda s: int(s) if s.lstrip("-").isdigit() else None, toks)'
        ),
        "note": (
            "mapMaybe fuses parse-and-filter: the parser answers a value or None, and the Nones are "
            "dropped in one pass. lstrip('-') lets a single leading minus through. O(n)."
        ),
    },
    {
        "id": "4.5",
        "level": "drill",
        "title": "Stutter",
        "statement": (
            "Return a new list in which every element of the input appears twice in a row, in order."
        ),
        "contract": "duplicate_each(xs: list) -> list",
        "tests": """
>>> duplicate_each([1, 2])
[1, 1, 2, 2]
>>> duplicate_each([])
[]
>>> duplicate_each(["a"])
['a', 'a']
""",
        "solution": "duplicate_each = lambda xs: concatMap(lambda x: [x, x], xs)",
        "note": (
            "concatMap maps each element to a LITTLE LIST and flattens the results in one step -- "
            "the shape for 'each input yields several outputs'. O(n)."
        ),
    },
    # ---------------------------------------------------------------- apply
    {
        "id": "4.6",
        "level": "apply",
        "title": "Clean the sensor feed",
        "statement": (
            "A sensor feed is a list of readings in which dropped samples appear as None. Return the\n"
            "pair (good, dropped): the list of surviving readings in order, and how many were None."
        ),
        "contract": "clean_readings(readings: list) -> tuple",
        "tests": """
>>> clean_readings([1, None, 2, None, 3])
([1, 2, 3], 2)
>>> clean_readings([None, None])
([], 2)
>>> clean_readings([4, 5])
([4, 5], 0)
""",
        "solution": (
            "def clean_readings(readings):\n"
            "    good = catMaybes(readings)\n"
            "    return (good, len(readings) - len(good))"
        ),
        "note": (
            "catMaybes drops the Nones (it is mapMaybe with the identity); the drop count is the "
            "length difference. O(n)."
        ),
    },
    {
        "id": "4.7",
        "level": "apply",
        "title": "Line-item totals",
        "statement": (
            "An order has parallel arrays of unit prices and quantities. Return the total for each\n"
            "line item (price times quantity), position by position. If the arrays differ in length,\n"
            "the shorter one governs."
        ),
        "contract": "line_totals(prices: list, quantities: list) -> list",
        "tests": """
>>> line_totals([2, 3, 5], [4, 1, 2])
[8, 3, 10]
>>> line_totals([2, 3, 5], [4])
[8]
>>> line_totals([], [])
[]
""",
        "solution": "line_totals = lambda prices, quantities: zipWith(lambda p, q: p * q, prices, "
                    "quantities)",
        "note": (
            "zipWith combines two lists elementwise with a function, stopping at the shorter -- the "
            "go-to for 'do X to matching positions of two arrays'. O(n)."
        ),
    },
    {
        "id": "4.8",
        "level": "apply",
        "title": "Three-column totals",
        "statement": (
            "An invoice has three parallel columns: base price, tax, and tip. Return the grand total\n"
            "for each row by summing the three columns position by position."
        ),
        "contract": "row_totals(base: list, tax: list, tip: list) -> list",
        "tests": """
>>> row_totals([10, 20], [1, 2], [2, 3])
[13, 25]
>>> row_totals([10], [1], [2])
[13]
>>> row_totals([], [], [])
[]
""",
        "solution": "row_totals = lambda base, tax, tip: zipWith3(lambda b, t, p: b + t + p, base, tax, "
                    "tip)",
        "note": (
            "zipWith3 is zipWith for three lists at once -- no intermediate tuples. O(n)."
        ),
    },
    {
        "id": "4.9",
        "level": "apply",
        "title": "Rectangle areas",
        "statement": (
            "Given a list of rectangles, each a (width, height) pair, return the area of each\n"
            "rectangle in order."
        ),
        "contract": "areas(rects: list) -> list",
        "tests": """
>>> areas([(2, 3), (4, 5)])
[6, 20]
>>> areas([(0, 9)])
[0]
>>> areas([])
[]
""",
        "solution": "areas = lambda rects: starmap(lambda w, h: w * h, rects)",
        "note": (
            "starmap spreads each tuple across a multi-argument function -- map_ composed with "
            "uncurry, so the (w, h) pairs unpack straight into the lambda. O(n)."
        ),
    },
    {
        "id": "4.10",
        "level": "apply",
        "title": "Merge the playlists",
        "statement": (
            "Given several playlists, each a list of song titles, merge them into one playlist in\n"
            "order, then remove duplicate songs keeping the first appearance of each."
        ),
        "contract": "merge_playlists(playlists: list) -> list",
        "tests": """
>>> merge_playlists([["a", "b"], ["b", "c"], ["a"]])
['a', 'b', 'c']
>>> merge_playlists([])
[]
>>> merge_playlists([[], ["solo"]])
['solo']
""",
        "solution": "merge_playlists = lambda playlists: nub(concat(playlists))",
        "note": (
            "concat flattens the list of lists by one level; nub then drops repeats keeping first "
            "occurrence. O(total songs)."
        ),
    },
    # ---------------------------------------------------------------- challenge
    {
        "id": "4.11",
        "level": "challenge",
        "title": "Affordable outfits",
        "statement": (
            "A wardrobe has shirts and pants, each an (name, price) pair. Generate every\n"
            "shirt-and-pant outfit, keep only those whose combined price is within a budget, and\n"
            "return them as (shirt_name, pant_name) pairs in generation order (shirts outer, pants\n"
            "inner)."
        ),
        "contract": "affordable_outfits(shirts: list, pants: list, budget: int) -> list",
        "tests": """
>>> shirts = [("red", 20), ("blue", 30)]
>>> pants = [("a", 40), ("b", 10)]
>>> affordable_outfits(shirts, pants, 45)
[('red', 'b'), ('blue', 'b')]
>>> affordable_outfits(shirts, pants, 5)
[]
>>> affordable_outfits([], pants, 100)
[]
""",
        "solution": (
            "def affordable_outfits(shirts, pants, budget):\n"
            "    pairs = cross(shirts, pants)\n"
            "    ok = filter_(lambda pr: pr[0][1] + pr[1][1] <= budget, pairs)\n"
            "    return [(s[0], p[0]) for s, p in ok]"
        ),
        "note": (
            "cross is the Cartesian product -- every (shirt, pant) combination; filter_ keeps the "
            "affordable ones; a comprehension pulls the names out. O(len(shirts)*len(pants))."
        ),
    },
    {
        "id": "4.12",
        "level": "challenge",
        "title": "Inventory reconciliation",
        "statement": (
            "An inventory log is a list of transaction strings. Each is an item name optionally led\n"
            "by a sign: '+apple' or 'apple' is an addition, '-banana' is a removal. Blank strings are\n"
            "skipped. Parse the log, then return the pair (added, removed): the item names that were\n"
            "added and the item names that were removed, each in the order they appeared in the log."
        ),
        "contract": "reconcile(txns: list) -> tuple",
        "tests": """
>>> reconcile(["+apple", "-banana", "cherry", "", "-apple"])
(['apple', 'cherry'], ['banana', 'apple'])
>>> reconcile(["", "  "])
([], [])
>>> reconcile(["milk", "-milk"])
(['milk'], ['milk'])
""",
        "solution": (
            "def reconcile(txns):\n"
            "    def parse(t):\n"
            "        t = t.strip()\n"
            "        if not t:\n"
            "            return None\n"
            "        if t[0] == '-':\n"
            "            return (-1, t[1:])\n"
            "        if t[0] == '+':\n"
            "            return (1, t[1:])\n"
            "        return (1, t)\n"
            "    signed = mapMaybe(parse, txns)\n"
            "    adds, rems = partition(lambda sr: sr[0] > 0, signed)\n"
            "    return ([item for _, item in adds], [item for _, item in rems])"
        ),
        "note": (
            "mapMaybe parses each line to a (sign, item) record and drops the blanks; partition "
            "splits additions from removals in one pass; comprehensions strip the sign back off. "
            "O(n). The common bug is treating a bare 'apple' as malformed rather than an addition."
        ),
    },
]
