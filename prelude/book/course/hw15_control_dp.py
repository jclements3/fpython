CHAPTER = 15
TITLE = "Control and Dynamic Programming"

ITEMS = [
{
 "id": "15.1", "level": "drill", "title": "Tribonacci",
 "statement": "The tribonacci sequence starts 0, 1, 1 and every later term is the sum of the previous\n"
              "THREE. Write trib(n) with @memo so large n is instant. State the recurrence before "
              "coding.",
 "contract": "trib(n: int) -> int",
 "tests": ">>> trib(0), trib(1), trib(2)\n(0, 1, 1)\n>>> trib(4)\n4\n>>> trib(10)\n149\n"
          ">>> trib(25)\n1389537",
 "solution": "@memo\n"
             "def trib(n):\n"
             "    return n if n < 2 else 1 if n == 2 else trib(n - 1) + trib(n - 2) + trib(n - 3)",
 "note": "Direct recurrence plus memo; O(n) states, O(1) work each. Without memo this is O(3^n) -- "
         "the whole lesson in one decorator.",
},
{
 "id": "15.2", "level": "drill", "title": "First power of two",
 "statement": "Using until, return the smallest power of two that is >= n (n >= 1). No loops of your\n"
              "own: state the stop predicate and the step, let until iterate.",
 "contract": "first_pow2(n: int) -> int",
 "tests": ">>> first_pow2(1)\n1\n>>> first_pow2(100)\n128\n>>> first_pow2(128)\n128\n"
          ">>> first_pow2(1025)\n2048",
 "solution": "first_pow2 = lambda n: until(lambda x: x >= n, lambda x: 2 * x, 1)",
 "note": "until(stop, step, seed) is a while loop as an expression. O(log n) doublings.",
},
{
 "id": "15.3", "level": "drill", "title": "Digital root",
 "statement": "The digital root of n repeatedly replaces n with the sum of its digits until a single\n"
              "digit remains. Write it with until -- the fixed point is 'already one digit'.",
 "contract": "digital_root(n: int) -> int",
 "tests": ">>> digital_root(0)\n0\n>>> digital_root(7)\n7\n>>> digital_root(9875)\n2\n"
          ">>> digital_root(99999)\n9",
 "solution": "digital_root = lambda n: until(lambda x: x < 10, lambda x: sum(map(int, str(x))), n)",
 "note": "Stop predicate x < 10; the step is one digit-sum. Each step shrinks the number fast, so "
         "only a handful of iterations ever run.",
},
{
 "id": "15.4", "level": "drill", "title": "Staircase, three strides",
 "statement": "You climb a staircase of n steps taking 1, 2 or 3 steps at a time. Count the ways to\n"
              "reach the top (distinct ordered stride sequences) with a memoized recursion; ways(0)\n"
              "is 1 (stand still), negative overshoot is 0.",
 "contract": "steps3(n: int) -> int",
 "tests": ">>> steps3(0)\n1\n>>> steps3(1)\n1\n>>> steps3(4)\n7\n>>> steps3(10)\n274",
 "solution": "@memo\n"
             "def steps3(n):\n"
             "    if n == 0:\n"
             "        return 1\n"
             "    if n < 0:\n"
             "        return 0\n"
             "    return steps3(n - 1) + steps3(n - 2) + steps3(n - 3)",
 "note": "The two base cases ARE the specification: one way to be done, no way to overshoot. "
         "O(n) states.",
},
{
 "id": "15.5", "level": "drill", "title": "Reading the DP table",
 "statement": "Write fib with @memo inside a helper, compute fib(n), and return the pair\n"
              "(fib(n), number_of_cached_states). The cache IS the DP table; its size is the state\n"
              "count that complexity analysis asks you to say out loud.",
 "contract": "fib_with_table(n: int) -> tuple[int, int]",
 "tests": ">>> fib_with_table(0)\n(0, 1)\n>>> fib_with_table(10)\n(55, 11)\n"
          ">>> fib_with_table(20)\n(6765, 21)",
 "solution": "def fib_with_table(n):\n"
             "    @memo\n"
             "    def fib(k):\n"
             "        return k if k < 2 else fib(k - 1) + fib(k - 2)\n"
             "    value = fib(n)\n"
             "    return (value, len(fib.cache))",
 "note": "memo exposes .cache precisely so the table is inspectable: n+1 states for fib(n). "
         "Defining the helper inside gives every call a fresh table.",
},
{
 "id": "15.6", "level": "apply", "title": "House robber",
 "statement": "A row of houses holds these amounts of cash. You cannot rob two ADJACENT houses.\n"
              "Return the maximum total you can take. Classic interview DP: at each house, rob it and\n"
              "skip a neighbour, or walk past.",
 "contract": "rob(xs: list[int]) -> int",
 "tests": ">>> rob([])\n0\n>>> rob([5])\n5\n>>> rob([1, 2, 3, 1])\n4\n>>> rob([2, 7, 9, 3, 1])\n12",
 "solution": "def rob(xs):\n"
             "    @memo\n"
             "    def go(i):\n"
             "        if i >= len(xs):\n"
             "            return 0\n"
             "        return max(go(i + 1), xs[i] + go(i + 2))\n"
             "    return go(0)",
 "note": "State: index; choice: take (jump 2) or skip (jump 1). O(n) states. The classic mistake "
         "is greedy on the largest house -- [2,7,9] breaks it.",
},
{
 "id": "15.7", "level": "apply", "title": "Decode ways",
 "statement": "A message of letters A-Z was encoded as digits (A=1 .. Z=26) and concatenated. Count\n"
              "the ways to decode a digit string: '12' is 2 ('AB' or 'L'). A leading zero at any\n"
              "decision point kills that branch; the empty string counts as one way.",
 "contract": "decode_ways(s: str) -> int",
 "tests": ">>> decode_ways('')\n1\n>>> decode_ways('12')\n2\n>>> decode_ways('226')\n3\n"
          ">>> decode_ways('06')\n0\n>>> decode_ways('11106')\n2",
 "solution": "def decode_ways(s):\n"
             "    @memo\n"
             "    def go(i):\n"
             "        if i == len(s):\n"
             "            return 1\n"
             "        if s[i] == '0':\n"
             "            return 0\n"
             "        two = go(i + 2) if i + 1 < len(s) and 10 <= int(s[i:i + 2]) <= 26 else 0\n"
             "        return go(i + 1) + two\n"
             "    return go(0)",
 "note": "State: position; two branches (one digit, two digits) guarded by the 10..26 window and "
         "the zero rule. O(n) states; the '0' guard is where most attempts die.",
},
{
 "id": "15.8", "level": "apply", "title": "Jump game",
 "statement": "xs[i] is the maximum jump length from index i. Starting at index 0, can you reach the\n"
              "last index? Solve it as one fold over enum(xs) carrying the furthest reachable index --\n"
              "poison the accumulator when an index is unreachable.",
 "contract": "can_jump(xs: list[int]) -> bool",
 "tests": ">>> can_jump([0])\nTrue\n>>> can_jump([2, 3, 1, 1, 4])\nTrue\n"
          ">>> can_jump([3, 2, 1, 0, 4])\nFalse\n>>> can_jump([1, 0, 1])\nFalse",
 "solution": "def can_jump(xs):\n"
             "    def step(far, ix):\n"
             "        i, x = ix\n"
             "        return -1 if far < 0 or far < i else max(far, i + x)\n"
             "    return foldl(step, enum(xs), 0) >= 0",
 "note": "Greedy reach as a fold; -1 is the poison value that propagates (the g9 trick on a number). "
         "O(n), no DP table needed -- reach is monotone.",
},
{
 "id": "15.9", "level": "apply", "title": "Perfect squares",
 "statement": "Return the fewest perfect squares (1, 4, 9, 16, ...) summing exactly to n.\n"
              "12 -> 3 (4+4+4), 13 -> 2 (4+9). Memoize on the remaining amount; isqrt bounds the\n"
              "candidates.",
 "contract": "num_squares(n: int) -> int",
 "tests": ">>> num_squares(0)\n0\n>>> num_squares(1)\n1\n>>> num_squares(12)\n3\n"
          ">>> num_squares(13)\n2\n>>> num_squares(7)\n4",
 "solution": "def num_squares(n):\n"
             "    @memo\n"
             "    def go(m):\n"
             "        if m == 0:\n"
             "            return 0\n"
             "        return min(1 + go(m - k * k) for k in range(1, isqrt(m) + 1))\n"
             "    return go(n)",
 "note": "Coin change with square coins; isqrt(m) trims the branch factor. O(n * sqrt(n)). "
         "Greedy (largest square first) fails on 12.",
},
{
 "id": "15.10", "level": "apply", "title": "Growth to target",
 "statement": "A town of pop people grows rate percent per year (integer floor) and then gains influx\n"
              "newcomers. Using until with a (population, years) state tuple, return how many whole\n"
              "years until the population reaches target (0 if already there).",
 "contract": "years_to_target(pop: int, rate: int, influx: int, target: int) -> int",
 "tests": ">>> years_to_target(500, 5, 10, 400)\n0\n>>> years_to_target(100, 10, 0, 200)\n8\n"
          ">>> years_to_target(1, 0, 10, 51)\n5",
 "solution": "def years_to_target(pop, rate, influx, target):\n"
             "    grow = lambda s: (s[0] * (100 + rate) // 100 + influx, s[1] + 1)\n"
             "    return snd(until(lambda s: s[0] >= target, grow, (pop, 0)))",
 "note": "The tuple state carries the counter alongside the value -- until's standard idiom. "
         "Integer arithmetic keeps the doctests exact.",
},
{
 "id": "15.11", "level": "challenge", "title": "Longest palindromic subsequence",
 "statement": "Return the length of the longest subsequence of s (not necessarily contiguous) that\n"
              "reads the same forwards and backwards. 'bbbab' -> 4 ('bbbb'). Memoize on the (i, j)\n"
              "window: matching ends extend the palindrome by two; otherwise drop one end.",
 "contract": "lps(s: str) -> int",
 "tests": ">>> lps('')\n0\n>>> lps('a')\n1\n>>> lps('bbbab')\n4\n>>> lps('cbbd')\n2\n"
          ">>> lps('abcdef')\n1",
 "solution": "def lps(s):\n"
             "    @memo\n"
             "    def go(i, j):\n"
             "        if i > j:\n"
             "            return 0\n"
             "        if i == j:\n"
             "            return 1\n"
             "        if s[i] == s[j]:\n"
             "            return 2 + go(i + 1, j - 1)\n"
             "        return max(go(i + 1, j), go(i, j - 1))\n"
             "    return go(0, len(s) - 1) if s else 0",
 "note": "The lcs skeleton on one string against itself, expressed as a shrinking window. "
         "O(n^2) states; the i == j base (a single char is a palindrome) is the easy one to forget.",
},
{
 "id": "15.12", "level": "challenge", "title": "Word break",
 "statement": "Can s be segmented into a sequence of words from the given list (words reusable)?\n"
              "'leetcode' with ['leet', 'code'] -> True. Memoize on the start index; isPrefixOf tests\n"
              "each candidate word against the remaining suffix.",
 "contract": "word_break(s: str, words: list[str]) -> bool",
 "tests": ">>> word_break('', ['a'])\nTrue\n>>> word_break('leetcode', ['leet', 'code'])\nTrue\n"
          ">>> word_break('applepenapple', ['apple', 'pen'])\nTrue\n"
          ">>> word_break('catsandog', ['cats', 'dog', 'sand', 'and', 'cat'])\nFalse\n"
          ">>> word_break('aaaaaaa', ['aaa', 'aaaa'])\nTrue",
 "solution": "def word_break(s, words):\n"
             "    ws = tuple(words)\n"
             "    @memo\n"
             "    def go(i):\n"
             "        if i == len(s):\n"
             "            return True\n"
             "        return any(isPrefixOf(w, s[i:]) and go(i + len(w)) for w in ws)\n"
             "    return go(0)",
 "note": "State: start index -- the future only needs where the unbroken suffix begins. any() "
         "short-circuits; memo caps the work at O(len(s) * len(words)) prefix checks.",
},
]
