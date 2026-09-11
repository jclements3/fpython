CHAPTER = 3
TITLE = "Lists I: The Basics"

ITEMS = [
    # ---------------------------------------------------------------- drills
    {
        "id": "3.1",
        "level": "drill",
        "title": "Swap the ends",
        "statement": (
            "Return a copy of a list (length >= 2) with its first and last elements swapped and\n"
            "everything in between left alone. Build it from the end-taking tools, not by index."
        ),
        "contract": "swap_ends(xs: list) -> list",
        "tests": """
>>> swap_ends([1, 2, 3, 4])
[4, 2, 3, 1]
>>> swap_ends([1, 2])
[2, 1]
>>> swap_ends([5, 9, 9, 5])
[5, 9, 9, 5]
""",
        "solution": "swap_ends = lambda xs: [last(xs)] + init(tail(xs)) + [head(xs)]",
        "note": (
            "head/last read the ends; init(tail(xs)) is the middle (drop one from each side). "
            "O(n) to rebuild. The classic slip is writing xs[1:-1] and forgetting it is empty for "
            "length-2 input -- init(tail(...)) handles that for free."
        ),
    },
    {
        "id": "3.2",
        "level": "drill",
        "title": "Deal the deck",
        "statement": (
            "Deal a list into two halves. With an odd length the extra element goes to the SECOND\n"
            "half. Return the pair of halves."
        ),
        "contract": "deal(xs: list) -> tuple",
        "tests": """
>>> deal([1, 2, 3, 4])
([1, 2], [3, 4])
>>> deal([1, 2, 3])
([1], [2, 3])
>>> deal([])
([], [])
""",
        "solution": "deal = lambda xs: splitAt(len(xs) // 2, xs)",
        "note": (
            "splitAt(n, xs) cuts into (xs[:n], xs[n:]) in one call; floor division sends the odd "
            "element rightward. O(n)."
        ),
    },
    {
        "id": "3.3",
        "level": "drill",
        "title": "Adjacent duplicate",
        "statement": (
            "Report whether any two neighbouring elements of a list are equal. Empty and\n"
            "single-element lists have no neighbours, so the answer is False."
        ),
        "contract": "has_adjacent_dup(xs: list) -> bool",
        "tests": """
>>> has_adjacent_dup([1, 2, 2, 3])
True
>>> has_adjacent_dup([1, 2, 3])
False
>>> has_adjacent_dup([])
False
>>> has_adjacent_dup([5])
False
""",
        "solution": "has_adjacent_dup = lambda xs: any(a == b for a, b in pairwise(xs))",
        "note": (
            "pairwise turns a list into its consecutive pairs -- exactly the shape any rule about "
            "neighbours wants. It yields nothing for length < 2, so any(...) is False there. O(n)."
        ),
    },
    {
        "id": "3.4",
        "level": "drill",
        "title": "Count the distinct",
        "statement": (
            "Count how many distinct values a list contains. Order does not matter; duplicates\n"
            "count once."
        ),
        "contract": "count_distinct(xs: list) -> int",
        "tests": """
>>> count_distinct([1, 2, 2, 3, 1])
3
>>> count_distinct([])
0
>>> count_distinct([7, 7, 7])
1
""",
        "solution": "count_distinct = lambda xs: len(nub(xs))",
        "note": (
            "nub keeps first occurrences (elements must be hashable); its length is the distinct "
            "count. O(n). set(xs) would work too but nub is the order-preserving habit."
        ),
    },
    {
        "id": "3.5",
        "level": "drill",
        "title": "Phone book lookup",
        "statement": (
            "A phone book is a list of (name, number) pairs. Look up a name and return its number,\n"
            "or a supplied default string when the name is absent."
        ),
        "contract": "lookup_or(book: list, name, default) -> value",
        "tests": """
>>> book = [("ada", "123"), ("bob", "456")]
>>> lookup_or(book, "bob", "unknown")
'456'
>>> lookup_or(book, "cy", "unknown")
'unknown'
>>> lookup_or([], "ada", "unknown")
'unknown'
""",
        "solution": "lookup_or = lambda book, name, default: fromMaybe(default, lookup(name, book))",
        "note": (
            "lookup returns the first match or None; fromMaybe supplies the fallback. The pairing "
            "of a None-returning search with fromMaybe is the whole Maybe idiom in one line."
        ),
    },
    # ---------------------------------------------------------------- apply
    {
        "id": "3.6",
        "level": "apply",
        "title": "Spreadsheet column totals",
        "statement": (
            "A spreadsheet is a list of rows, each row a list of numbers. Rows may be ragged (some\n"
            "shorter than others). Return the total of each column; a short row simply contributes\n"
            "nothing to columns it does not reach. An empty sheet has no columns."
        ),
        "contract": "column_sums(grid: list) -> list",
        "tests": """
>>> column_sums([[1, 2, 3], [4, 5, 6]])
[5, 7, 9]
>>> column_sums([[1, 2, 3], [4, 5]])
[5, 7, 3]
>>> column_sums([])
[]
""",
        "solution": (
            "column_sums = lambda grid: [] if null(grid) else [sum(col) for col in transpose(grid)]"
        ),
        "note": (
            "transpose is ragged-safe: short rows drop out of later columns instead of truncating "
            "every column to the shortest row. null guards the empty sheet. O(cells)."
        ),
    },
    {
        "id": "3.7",
        "level": "apply",
        "title": "Mastermind hits",
        "statement": (
            "In Mastermind a guess and the secret code are equal-length sequences. Count the\n"
            "positions where the guess matches the secret exactly (the 'exact hits')."
        ),
        "contract": "matches(guess: list, secret: list) -> int",
        "tests": """
>>> matches([1, 2, 3, 4], [1, 0, 3, 0])
2
>>> matches("abc", "abc")
3
>>> matches([], [])
0
""",
        "solution": "matches = lambda guess, secret: sum(1 for a, b in zip_(guess, secret) if a == b)",
        "note": (
            "zip_ walks both sequences in lockstep, stopping at the shorter; count the agreeing "
            "positions. O(n). zip_ returns a real list, so it also works on strings."
        ),
    },
    {
        "id": "3.8",
        "level": "apply",
        "title": "Strip a log tag",
        "statement": (
            "Log lines sometimes begin with a fixed tag such as 'ERROR:'. Remove that leading tag\n"
            "if the line starts with it; otherwise return the line unchanged."
        ),
        "contract": "strip_tag(tag: str, line: str) -> str",
        "tests": """
>>> strip_tag("ERROR:", "ERROR:disk full")
'disk full'
>>> strip_tag("ERROR:", "all good")
'all good'
>>> strip_tag("", "unchanged")
'unchanged'
""",
        "solution": "strip_tag = lambda tag, line: fromMaybe(line, stripPrefix(tag, line))",
        "note": (
            "stripPrefix returns the remainder after the tag, or None when the tag is absent; "
            "fromMaybe falls back to the whole line. An empty tag matches and strips nothing."
        ),
    },
    {
        "id": "3.9",
        "level": "apply",
        "title": "Filter by prefix and suffix",
        "statement": (
            "Given a list of filenames, keep exactly those that both start with a required prefix\n"
            "and end with a required extension. Empty prefix or suffix matches everything."
        ),
        "contract": "by_affix(names: list, prefix: str, suffix: str) -> list",
        "tests": """
>>> by_affix(["test_a.py", "test_b.txt", "main.py"], "test_", ".py")
['test_a.py']
>>> by_affix(["a", "b"], "", "")
['a', 'b']
>>> by_affix(["main.py"], "test_", ".py")
[]
""",
        "solution": (
            "by_affix = lambda names, prefix, suffix: [n for n in names\n"
            "                                          if isPrefixOf(prefix, n)\n"
            "                                          and isSuffixOf(suffix, n)]"
        ),
        "note": (
            "isPrefixOf / isSuffixOf work on strings and lists alike. Note isSuffixOf uses the "
            "len-based slice, not xs[-len(p):], so an empty suffix correctly matches all. O(n*k)."
        ),
    },
    {
        "id": "3.10",
        "level": "apply",
        "title": "Pad a scoreboard",
        "statement": (
            "A scoreboard must show exactly n slots. Given the current entries, pad on the right\n"
            "with a fill value until the list has length n. If it is already n or longer, leave it\n"
            "unchanged (never truncate)."
        ),
        "contract": "pad_to(xs: list, n: int, fill) -> list",
        "tests": """
>>> pad_to([1, 2], 4, 0)
[1, 2, 0, 0]
>>> pad_to([1, 2, 3], 2, 0)
[1, 2, 3]
>>> pad_to([], 3, "-")
['-', '-', '-']
""",
        "solution": "pad_to = lambda xs, n, fill: xs + replicate(max(n - len(xs), 0), fill)",
        "note": (
            "replicate(k, fill) makes k copies; max(..., 0) means an already-long list gets zero "
            "padding rather than a negative count. O(n)."
        ),
    },
    # ---------------------------------------------------------------- challenge
    {
        "id": "3.11",
        "level": "challenge",
        "title": "Roster reconciliation",
        "statement": (
            "An event keeps a list of previous attendees and a list of this time's check-ins (which\n"
            "may contain repeats). Produce three things: the DISTINCT current attendees who also\n"
            "attended before ('returning'), the distinct current attendees who did not ('newcomers'),\n"
            "and a flag that is True when there were no previous attendees at all. Preserve the\n"
            "first-seen order of the current check-ins in both lists."
        ),
        "contract": "roster_diff(prev: list, curr: list) -> tuple",
        "tests": """
>>> roster_diff(["ada", "bob"], ["bob", "cy", "cy", "ada", "dee"])
(['bob', 'ada'], ['cy', 'dee'], False)
>>> roster_diff([], ["ada", "ada", "bob"])
([], ['ada', 'bob'], True)
>>> roster_diff(["x"], [])
([], [], False)
""",
        "solution": (
            "def roster_diff(prev, curr):\n"
            "    distinct = nub(curr)\n"
            "    returning = [x for x in distinct if elem(x, prev)]\n"
            "    newcomers = [x for x in distinct if notElem(x, prev)]\n"
            "    return (returning, newcomers, null(prev))"
        ),
        "note": (
            "nub gives the distinct current names in first-seen order; elem / notElem split them "
            "against the previous roster; null reports the empty-history case. O(len(curr)*len(prev)) "
            "with lists -- a set(prev) would make membership O(1) if prev were large."
        ),
    },
    {
        "id": "3.12",
        "level": "challenge",
        "title": "Shipping manifest",
        "statement": (
            "A shipping manifest is built from three parallel arrays: item names, weights, and bin\n"
            "labels (equal length). Combine them into records, skip the first `skip` records (already\n"
            "shipped), then number the remaining records from 1. Return the pair (numbered, total)\n"
            "where numbered is a list of (rank, name) and total is the summed weight of the kept\n"
            "records. Skipping past the end yields ([], 0)."
        ),
        "contract": "manifest(names: list, weights: list, bins: list, skip: int) -> tuple",
        "tests": """
>>> manifest(["a", "b", "c"], [10, 20, 30], ["x", "y", "z"], 1)
([(1, 'b'), (2, 'c')], 50)
>>> manifest(["a", "b", "c"], [10, 20, 30], ["x", "y", "z"], 0)
([(1, 'a'), (2, 'b'), (3, 'c')], 60)
>>> manifest(["a"], [10], ["x"], 5)
([], 0)
""",
        "solution": (
            "def manifest(names, weights, bins, skip):\n"
            "    records = zip3(names, weights, bins)\n"
            "    kept = drop(skip, records)\n"
            "    numbered = [(i, r[0]) for i, r in enum(kept, 1)]\n"
            "    cols = unzip(kept)\n"
            "    total = sum(cols[1]) if kept else 0\n"
            "    return (numbered, total)"
        ),
        "note": (
            "zip3 stitches the parallel arrays into records; drop discards the shipped prefix; "
            "enum(..., 1) numbers from 1; unzip splits the kept records back into columns so the "
            "weight column can be summed. O(n)."
        ),
    },
]
