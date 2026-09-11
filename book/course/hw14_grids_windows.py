CHAPTER = 14
TITLE = "Grids and Windows"

ITEMS = [
{
 "id": "14.1", "level": "drill", "title": "How many neighbours?",
 "statement": "Return how many in-bounds orthogonal neighbours cell (r, c) has in an R-by-C grid.\n"
              "neighbors4 already does the bounds checking -- you just count what it yields.",
 "contract": "degree(r: int, c: int, R: int, C: int) -> int",
 "tests": ">>> degree(0, 0, 2, 2)\n"
          "2\n"
          ">>> degree(0, 1, 3, 3)\n"
          "3\n"
          ">>> degree(1, 1, 3, 3)\n"
          "4\n"
          ">>> degree(0, 0, 1, 1)\n"
          "0",
 "solution": "degree = lambda r, c, R, C: len(list(neighbors4(r, c, R, C)))",
 "note": "neighbors4 is a generator, so list() it before len(). Corners have 2, edges 3, interior "
         "4 -- and a 1x1 grid has none.",
},
{
 "id": "14.2", "level": "drill", "title": "Diagonal neighbours only",
 "statement": "Return the DIAGONAL in-bounds neighbours of (r, c), sorted. You own two neighbour\n"
              "generators; the diagonals are exactly what one yields and the other does not.",
 "contract": "diag_neighbors(r: int, c: int, R: int, C: int) -> list[tuple[int, int]]",
 "tests": ">>> diag_neighbors(0, 0, 3, 3)\n"
          "[(1, 1)]\n"
          ">>> diag_neighbors(1, 1, 3, 3)\n"
          "[(0, 0), (0, 2), (2, 0), (2, 2)]\n"
          ">>> diag_neighbors(0, 1, 1, 3)\n"
          "[]",
 "solution": "diag_neighbors = lambda r, c, R, C: sorted(\n"
             "    set(neighbors8(r, c, R, C)) - set(neighbors4(r, c, R, C)))",
 "note": "Set difference of the 8-neighbourhood and the 4-neighbourhood, sorted for a "
         "deterministic answer. A 1-row grid has no diagonals at all.",
},
{
 "id": "14.3", "level": "drill", "title": "Live neighbours",
 "statement": "A Game-of-Life board is a list of '0'/'1' strings. Count the live cells among the\n"
              "8-neighbourhood of (r, c).",
 "contract": "live_around(grid: list[str], r: int, c: int) -> int",
 "tests": ">>> board = ['111', '101', '111']\n"
          ">>> live_around(board, 1, 1)\n"
          "8\n"
          ">>> live_around(board, 0, 0)\n"
          "2\n"
          ">>> live_around(['1'], 0, 0)\n"
          "0",
 "solution": "live_around = lambda grid, r, c: sum(\n"
             "    grid[nr][nc] == '1' for nr, nc in neighbors8(r, c, len(grid), len(grid[0])))",
 "note": "sum over a generator of booleans counts the Trues; bounds live inside neighbors8, so no "
         "edge special-cases. This is the inner loop of every Life step.",
},
{
 "id": "14.4", "level": "drill", "title": "Longest positive stretch",
 "statement": "Given daily profit/loss numbers, find the length of the longest run of strictly\n"
              "positive days. Use longest_window: the state you must track is how many non-positive\n"
              "values sit inside the current window.",
 "contract": "longest_positive(xs: list[int]) -> int",
 "tests": ">>> longest_positive([1, 2, -1, 3, 4, 5])\n"
          "3\n"
          ">>> longest_positive([-1, -2])\n"
          "0\n"
          ">>> longest_positive([])\n"
          "0\n"
          ">>> longest_positive([5, 6])\n"
          "2",
 "solution": "def longest_positive(xs):\n"
             "    bad = [0]\n"
             "    def add(x): bad[0] += x <= 0\n"
             "    def rem(x): bad[0] -= x <= 0\n"
             "    return longest_window(xs, lambda: bad[0] == 0, add, rem)",
 "note": "State = a count of offenders in the window; valid means zero offenders. The one-element "
         "list is the standard closure-mutable-int idiom. O(n).",
},
{
 "id": "14.5", "level": "drill", "title": "Cells on the border",
 "statement": "How many cells of an R-by-C grid lie on its border? Characterise the border through\n"
              "neighbours: a border cell is one with fewer than 4 orthogonal neighbours.",
 "contract": "border_count(R: int, C: int) -> int",
 "tests": ">>> border_count(1, 1)\n"
          "1\n"
          ">>> border_count(2, 3)\n"
          "6\n"
          ">>> border_count(3, 3)\n"
          "8\n"
          ">>> border_count(1, 5)\n"
          "5",
 "solution": "border_count = lambda R, C: len(\n"
             "    [1 for r in range(R) for c in range(C) if len(list(neighbors4(r, c, R, C))) < 4])",
 "note": "Degree < 4 is exactly 'touches the edge'. O(R*C); the closed form 2R + 2C - 4 (clamped) "
         "is the optimisation to mention, not to start with.",
},
{
 "id": "14.6", "level": "apply", "title": "Count the islands",
 "statement": "A satellite tile is a list of '1'/'0' strings, land and water. Count the connected\n"
              "regions of land (orthogonal adjacency). Scan every cell; each unseen land cell starts\n"
              "a new island and a BFS flood that claims the rest of it.",
 "contract": "count_islands(grid: list[str]) -> int",
 "tests": ">>> count_islands(['11000', '11000', '00100'])\n"
          "2\n"
          ">>> count_islands(['101', '010', '101'])\n"
          "5\n"
          ">>> count_islands(['000'])\n"
          "0\n"
          ">>> count_islands(['1'])\n"
          "1",
 "solution": "def count_islands(grid):\n"
             "    R, C = len(grid), len(grid[0])\n"
             "    seen, n = set(), 0\n"
             "    for r in range(R):\n"
             "        for c in range(C):\n"
             "            if grid[r][c] == '1' and (r, c) not in seen:\n"
             "                n += 1\n"
             "                q = deque([(r, c)])\n"
             "                seen.add((r, c))\n"
             "                while len(q):\n"
             "                    y, x = q.popleft()\n"
             "                    for ny, nx in neighbors4(y, x, R, C):\n"
             "                        if grid[ny][nx] == '1' and (ny, nx) not in seen:\n"
             "                            seen.add((ny, nx))\n"
             "                            q.append((ny, nx))\n"
             "    return n",
 "note": "Outer scan + inner flood: every cell enters the queue at most once, O(R*C). Mark seen "
         "when ENQUEUING, not when popping, or the queue balloons with duplicates.",
},
{
 "id": "14.7", "level": "apply", "title": "At most k distinct products",
 "statement": "A shelf camera streams the product code seen each second, as a string of letters. Find\n"
              "the longest stretch showing at most k DISTINCT products. Window state: per-code counts\n"
              "plus how many codes are currently present.",
 "contract": "longest_at_most_k(s: str, k: int) -> int",
 "tests": ">>> longest_at_most_k('eceba', 2)\n"
          "3\n"
          ">>> longest_at_most_k('aa', 1)\n"
          "2\n"
          ">>> longest_at_most_k('aabbcc', 1)\n"
          "2\n"
          ">>> longest_at_most_k('abc', 0)\n"
          "0",
 "solution": "def longest_at_most_k(s, k):\n"
             "    counts, distinct = Tree(1, int), [0]\n"
             "    def add(c):\n"
             "        counts[c] += 1\n"
             "        distinct[0] += counts[c] == 1\n"
             "    def rem(c):\n"
             "        counts[c] -= 1\n"
             "        distinct[0] -= counts[c] == 0\n"
             "    return longest_window(s, lambda: distinct[0] <= k, add, rem)",
 "note": "distinct moves only when a count crosses 0<->1 -- that boundary bookkeeping is the whole "
         "problem. k = 0 forces the window empty forever: answer 0. O(n).",
},
{
 "id": "14.8", "level": "apply", "title": "Longest run within budget",
 "statement": "Task durations stream in (non-negative). What is the longest run of CONSECUTIVE tasks\n"
              "whose total fits in a time budget? Window state: the running sum.",
 "contract": "longest_within_budget(xs: list[int], budget: int) -> int",
 "tests": ">>> longest_within_budget([2, 1, 3, 4], 6)\n"
          "3\n"
          ">>> longest_within_budget([5], 3)\n"
          "0\n"
          ">>> longest_within_budget([], 10)\n"
          "0\n"
          ">>> longest_within_budget([1, 1, 1, 1], 2)\n"
          "2",
 "solution": "def longest_within_budget(xs, budget):\n"
             "    total = [0]\n"
             "    def add(x): total[0] += x\n"
             "    def rem(x): total[0] -= x\n"
             "    return longest_window(xs, lambda: total[0] <= budget, add, rem)",
 "note": "Shrinking is only sound because durations are non-negative (removing can never make the "
         "sum worse) -- say that invariant out loud; with negatives this window logic breaks.",
},
{
 "id": "14.9", "level": "apply", "title": "Island perimeter",
 "statement": "One island of '1' cells sits in a '0' sea. Its perimeter is the number of unit edges\n"
              "touching water or the map border. Count per land cell: 4 minus its LAND neighbours\n"
              "(off-grid sides count as water automatically, since neighbors4 never yields them).",
 "contract": "island_perimeter(grid: list[str]) -> int",
 "tests": ">>> island_perimeter(['0100', '1110', '0100'])\n"
          "12\n"
          ">>> island_perimeter(['1'])\n"
          "4\n"
          ">>> island_perimeter(['11'])\n"
          "6\n"
          ">>> island_perimeter(['00'])\n"
          "0",
 "solution": "def island_perimeter(grid):\n"
             "    R, C = len(grid), len(grid[0])\n"
             "    return sum(4 - sum(grid[nr][nc] == '1' for nr, nc in neighbors4(r, c, R, C))\n"
             "               for r in range(R) for c in range(C) if grid[r][c] == '1')\n",
 "note": "Each land cell contributes 4 edges minus one per land neighbour; the bounds-checked "
         "generator makes border edges fall out for free. O(R*C), no flood needed.",
},
{
 "id": "14.10", "level": "apply", "title": "Flood clock",
 "statement": "Water enters an open grid ('.' floor, '#' wall) at the top-left and spreads one\n"
              "orthogonal step per minute. Return the minute the LAST reachable floor cell gets wet\n"
              "(0 if only the entrance), or -1 if the entrance itself is a wall.",
 "contract": "flood_minutes(grid: list[str]) -> int",
 "tests": ">>> flood_minutes(['..', '..'])\n"
          "2\n"
          ">>> flood_minutes(['.'])\n"
          "0\n"
          ">>> flood_minutes(['#.'])\n"
          "-1\n"
          ">>> flood_minutes(['.#.', '...', '.#.'])\n"
          "4",
 "solution": "def flood_minutes(grid):\n"
             "    R, C = len(grid), len(grid[0])\n"
             "    if grid[0][0] == '#':\n"
             "        return -1\n"
             "    dist = {(0, 0): 0}\n"
             "    q = deque([(0, 0)])\n"
             "    while len(q):\n"
             "        r, c = q.popleft()\n"
             "        for nr, nc in neighbors4(r, c, R, C):\n"
             "            if grid[nr][nc] == '.' and (nr, nc) not in dist:\n"
             "                dist[(nr, nc)] = dist[(r, c)] + 1\n"
             "                q.append((nr, nc))\n"
             "    return max(dist.values())",
 "note": "BFS eccentricity: the dist map doubles as the seen-set, and the answer is its maximum "
         "rather than a target lookup -- the same machine as shortest-path, read differently.",
},
{
 "id": "14.11", "level": "challenge", "title": "Best uptime with k repairs",
 "statement": "A service log is a list of 1s (up) and 0s (down). You may retroactively excuse at most\n"
              "k downtimes. What is the longest stretch that then reads fully up? Classic interview\n"
              "form: longest window containing at most k zeros.",
 "contract": "max_up_with_repairs(xs: list[int], k: int) -> int",
 "tests": ">>> max_up_with_repairs([1, 1, 0, 0, 1], 1)\n"
          "3\n"
          ">>> max_up_with_repairs([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2)\n"
          "6\n"
          ">>> max_up_with_repairs([1, 1, 0, 1], 0)\n"
          "2\n"
          ">>> max_up_with_repairs([], 3)\n"
          "0",
 "solution": "def max_up_with_repairs(xs, k):\n"
             "    zeros = [0]\n"
             "    def add(x): zeros[0] += x == 0\n"
             "    def rem(x): zeros[0] -= x == 0\n"
             "    return longest_window(xs, lambda: zeros[0] <= k, add, rem)",
 "note": "LeetCode 1004 in window form: track zeros in the window, legal while <= k. The insight "
         "worth voicing: you never 'use' repairs -- the window just tolerates k zeros. O(n).",
},
{
 "id": "14.12", "level": "challenge", "title": "Rotting oranges",
 "statement": "A crate map holds 0 (empty), 1 (fresh), 2 (rotten). Every minute, fresh oranges next\n"
              "to a rotten one (orthogonally) rot. Return the minutes until nothing fresh remains, or\n"
              "-1 if some fresh orange can never be reached. Multi-source BFS: seed the queue with\n"
              "EVERY rotten orange at minute 0.",
 "contract": "orange_minutes(grid: list[list[int]]) -> int",
 "tests": ">>> orange_minutes([[2, 1, 1], [1, 1, 0], [0, 1, 1]])\n"
          "4\n"
          ">>> orange_minutes([[2, 1, 1], [0, 1, 1], [1, 0, 1]])\n"
          "-1\n"
          ">>> orange_minutes([[0, 2]])\n"
          "0\n"
          ">>> orange_minutes([[1]])\n"
          "-1",
 "solution": "def orange_minutes(grid):\n"
             "    R, C = len(grid), len(grid[0])\n"
             "    rotten = [(r, c) for r in range(R) for c in range(C) if grid[r][c] == 2]\n"
             "    q = deque([(r, c, 0) for r, c in rotten])\n"
             "    seen = set(rotten)\n"
             "    fresh = sum(row.count(1) for row in grid)\n"
             "    minutes = 0\n"
             "    while len(q):\n"
             "        r, c, m = q.popleft()\n"
             "        minutes = max(minutes, m)\n"
             "        for nr, nc in neighbors4(r, c, R, C):\n"
             "            if grid[nr][nc] == 1 and (nr, nc) not in seen:\n"
             "                seen.add((nr, nc))\n"
             "                fresh -= 1\n"
             "                q.append((nr, nc, m + 1))\n"
             "    return -1 if fresh else minutes",
 "note": "Multi-source BFS is ordinary BFS with several starting points enqueued at time 0; the "
         "distance of the last fresh orange is the answer. Count fresh up front so unreachable "
         "ones are detectable -- the classic miss is returning minutes without that check.",
},
]
