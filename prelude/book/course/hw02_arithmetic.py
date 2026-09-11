CHAPTER = 2
TITLE = "Arithmetic and Logic"

ITEMS = [
{
 "id": "2.1", "level": "drill", "title": "Parity census",
 "statement": "Count how many values are even and how many are odd, as a pair (evens, odds).\n"
              "Zero is even; negatives carry their usual parity.",
 "contract": "parity_counts(xs) -> (evens, odds)",
 "tests": ">>> parity_counts([1, 2, 3, 4])\n(2, 2)\n>>> parity_counts([])\n(0, 0)\n"
          ">>> parity_counts([-2, -3])\n(1, 1)\n>>> parity_counts([0])\n(1, 0)",
 "solution": "parity_counts = lambda xs: (sum(1 for x in xs if even(x)),\n"
             "                            sum(1 for x in xs if odd(x)))",
 "note": "Two generator sums over the parity predicates. One-pass with a fold is a fine alternative;\n"
         "the trap is forgetting that even(-2) and even(0) are True.",
},
{
 "id": "2.2", "level": "drill", "title": "Floor versus truncate",
 "statement": "Write both_divs(a, b) returning (div(a, b), quot(a, b)) so the two integer divisions\n"
              "can be compared side by side. They agree on positives and split on mixed signs.",
 "contract": "both_divs(a, b) -> (floored, truncated)",
 "tests": ">>> both_divs(7, 2)\n(3, 3)\n>>> both_divs(-7, 2)\n(-4, -3)\n"
          ">>> both_divs(7, -2)\n(-4, -3)\n>>> both_divs(-7, -2)\n(3, 3)",
 "solution": "both_divs = lambda a, b: (div(a, b), quot(a, b))",
 "note": "div floors toward negative infinity (Haskell/Python); quot truncates toward zero (C).\n"
         "Interviews live in the mixed-sign rows of this table.",
},
{
 "id": "2.3", "level": "drill", "title": "Character neighbours",
 "statement": "Using the Enum behaviour of succ and pred on characters, return the pair of codepoint\n"
              "neighbours of a character: (previous, next). Works on letters and digits alike.",
 "contract": "char_neighbours(c) -> (prev_char, next_char)",
 "tests": ">>> char_neighbours('b')\n('a', 'c')\n>>> char_neighbours('m')\n('l', 'n')\n"
          ">>> char_neighbours('5')\n('4', '6')",
 "solution": "char_neighbours = lambda c: (pred(c), succ(c))",
 "note": "succ/pred dispatch on type: strings step through codepoints, numbers add one. That Enum\n"
         "duality is the whole drill.",
},
{
 "id": "2.4", "level": "drill", "title": "Perfect square test",
 "statement": "Decide whether a non-negative integer is a perfect square, with no floating point\n"
              "anywhere -- float sqrt lies for large inputs, isqrt does not.",
 "contract": "is_square(n) -> bool",
 "tests": ">>> is_square(16)\nTrue\n>>> is_square(17)\nFalse\n>>> is_square(0)\nTrue\n"
          ">>> is_square(10**18)\nTrue\n>>> is_square(10**18 + 1)\nFalse",
 "solution": "is_square = lambda n: isqrt(n) ** 2 == n",
 "note": "Round-trip through the integer square root. The 10**18 tests are exactly where\n"
         "float-based checks start failing.",
},
{
 "id": "2.5", "level": "drill", "title": "Coprime pairs",
 "statement": "Two integers are coprime when they share no factor beyond 1 -- that is, their gcd is\n"
              "exactly 1. Signs do not matter.",
 "contract": "coprime(a, b) -> bool",
 "tests": ">>> coprime(8, 15)\nTrue\n>>> coprime(6, 9)\nFalse\n>>> coprime(1, 99)\nTrue\n"
          ">>> coprime(-3, 4)\nTrue",
 "solution": "coprime = lambda a, b: gcd(a, b) == 1",
 "note": "gcd is always >= 0 (Haskell semantics), so negative inputs need no special casing.",
},
{
 "id": "2.6", "level": "apply", "title": "Meeting end on a 24-hour clock",
 "statement": "A meeting starts at start_hour (0..23) and runs for duration hours, possibly negative\n"
              "(rescheduled earlier) or longer than a day. Return the ending hour on the 24-hour\n"
              "clock. Flooring mod does all the wrap-around work.",
 "contract": "end_hour(start, duration) -> hour in 0..23",
 "tests": ">>> end_hour(23, 2)\n1\n>>> end_hour(9, 8)\n17\n>>> end_hour(0, 48)\n0\n"
          ">>> end_hour(10, -12)\n22",
 "solution": "end_hour = lambda start, duration: mod(start + duration, 24)",
 "note": "mod's sign follows the divisor, so negative totals land in 0..23 automatically -- the\n"
         "reason floor-mod, not truncating rem, is the clock operator.",
},
{
 "id": "2.7", "level": "apply", "title": "Pages needed",
 "statement": "A report has n items and each page holds k. How many pages are needed? This is ceiling\n"
              "division, and the branch-free trick is to floor-divide the NEGATION: -div(-n, k).",
 "contract": "pages(n, k) -> int",
 "tests": ">>> pages(10, 3)\n4\n>>> pages(9, 3)\n3\n>>> pages(0, 5)\n0\n>>> pages(1, 10)\n1",
 "solution": "pages = lambda n, k: -div(-n, k)",
 "note": "ceil(n/k) == -floor(-n/k). The common alternative div(n + k - 1, k) also works; both beat\n"
         "importing math.ceil and converting through floats.",
},
{
 "id": "2.8", "level": "apply", "title": "Reduced aspect ratio",
 "statement": "Given a screen's width and height in pixels, report its aspect ratio in lowest terms\n"
              "as a pair. 1920x1080 is famously 16:9.",
 "contract": "ratio(w, h) -> (w_reduced, h_reduced)",
 "tests": ">>> ratio(1920, 1080)\n(16, 9)\n>>> ratio(100, 100)\n(1, 1)\n>>> ratio(7, 3)\n(7, 3)",
 "solution": "def ratio(w, h):\n"
             "    g = gcd(w, h)\n"
             "    return (div(w, g), div(h, g))",
 "note": "Divide both sides by the gcd -- the definition of lowest terms. O(log min(w, h)) from\n"
         "Euclid.",
},
{
 "id": "2.9", "level": "apply", "title": "Cron co-firing",
 "statement": "Two cron jobs fire every a minutes and every b minutes, and both just fired together.\n"
              "In how many minutes do they next fire together again? That is the least common\n"
              "multiple.",
 "contract": "next_together(a, b) -> minutes",
 "tests": ">>> next_together(4, 6)\n12\n>>> next_together(5, 7)\n35\n"
          ">>> next_together(10, 10)\n10\n>>> next_together(1, 9)\n9",
 "solution": "next_together = lcm",
 "note": "Recognize-it: the question IS lcm. Knowing lcm(a, b) = a * b / gcd(a, b) is the interview\n"
         "follow-up.",
},
{
 "id": "2.10", "level": "apply", "title": "Signal triage",
 "statement": "Sensor deltas arrive as integers. Triage them into (negative, zero, positive) counts\n"
              "using signum so the branching lives in arithmetic, not in if-chains.",
 "contract": "sign_census(xs) -> (negatives, zeros, positives)",
 "tests": ">>> sign_census([-2, 0, 3, 4])\n(1, 1, 2)\n>>> sign_census([])\n(0, 0, 0)\n"
          ">>> sign_census([0, 0])\n(0, 2, 0)",
 "solution": "def sign_census(xs):\n"
             "    signs = [signum(x) for x in xs]\n"
             "    return (signs.count(-1), signs.count(0), signs.count(1))",
 "note": "signum compresses the three-way comparison; count reads the census. One map, three counts,\n"
         "O(n).",
},
{
 "id": "2.11", "level": "challenge", "title": "Digital root",
 "statement": "The digital root of a non-negative integer repeatedly replaces the number by the sum\n"
              "of its digits until a single digit remains: 38 -> 11 -> 2. Compute it with integer\n"
              "arithmetic only -- no string conversion.",
 "contract": "digital_root(n) -> digit",
 "tests": ">>> digital_root(0)\n0\n>>> digital_root(9)\n9\n>>> digital_root(38)\n2\n"
          ">>> digital_root(12345)\n6\n>>> digital_root(999)\n9",
 "solution": "def digital_root(n):\n"
             "    while n > 9:\n"
             "        m, s = n, 0\n"
             "        while m:\n"
             "            m, r = divmod(m, 10)\n"
             "            s += r\n"
             "        n = s\n"
             "    return n",
 "note": "Digit-peeling via divmod inside a convergence loop. The slick closed form is\n"
         "0 if n == 0 else 1 + mod(n - 1, 9) -- casting out nines; mentioning it is a senior signal.",
},
{
 "id": "2.12", "level": "challenge", "title": "Visible lattice points",
 "statement": "Standing at the origin of an integer grid, the point (x, y) is visible when no other\n"
              "lattice point lies on the straight segment between you and it -- which happens exactly\n"
              "when gcd(x, y) == 1. The origin itself (gcd 0) is not visible. Count the visible\n"
              "points in a list.",
 "contract": "visible_count(points) -> int",
 "tests": ">>> visible_count([(1, 1), (2, 2), (0, 1), (0, 0), (3, 5)])\n3\n"
          ">>> visible_count([])\n0\n>>> visible_count([(0, 0)])\n0\n"
          ">>> visible_count([(1, 0), (0, 1)])\n2",
 "solution": "visible_count = lambda points: sum(1 for (x, y) in points if gcd(x, y) == 1)",
 "note": "A blocked point's coordinates share a factor g > 1 -- the blocker is (x/g, y/g). gcd's\n"
         ">= 0 semantics make negative quadrants free; gcd(0, 0) == 0 excludes the origin.",
},
]
