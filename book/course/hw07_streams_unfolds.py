CHAPTER = 7
TITLE = "Streams and Unfolds"

ITEMS = [
 {
  "id": "7.1",
  "level": "drill",
  "title": "First multiples",
  "statement": "Return the first n positive multiples of k, in order. Build the infinite stream of\n"
               "multiples with count and consume it with take -- no arithmetic on indices.",
  "contract": "multiples(k: int, n: int) -> list[int]",
  "tests": ">>> multiples(3, 4)\n[3, 6, 9, 12]\n>>> multiples(5, 1)\n[5]\n>>> multiples(2, 0)\n[]",
  "solution": "multiples = lambda k, n: take(n, count(k, k))",
  "note": "count(k, k) is the infinite stream k, 2k, 3k, ...; take stops it. O(n). Common mistake:\n"
          "reaching for range arithmetic when the stream says it directly.",
 },
 {
  "id": "7.2",
  "level": "drill",
  "title": "Banner line",
  "statement": "Build a banner string of n copies of a single character using repeat (the bounded,\n"
               "second-argument form) and join.",
  "contract": "banner(ch: str, n: int) -> str",
  "tests": ">>> banner('*', 3)\n'***'\n>>> banner('-', 0)\n''\n>>> banner('=', 5)\n'====='",
  "solution": "banner = lambda ch, n: \"\".join(repeat(ch, n))",
  "note": "repeat(x, n) is the finite form; join materialises it. O(n). Same result as ch * n --\n"
          "the point is knowing repeat's two modes.",
 },
 {
  "id": "7.3",
  "level": "drill",
  "title": "Powers table",
  "statement": "Return the first n powers of b starting at b**0, using iterate -- repeated\n"
               "multiplication as a stream, no ** operator.",
  "contract": "powers(b: int, n: int) -> list[int]",
  "tests": ">>> powers(2, 5)\n[1, 2, 4, 8, 16]\n>>> powers(10, 3)\n[1, 10, 100]\n>>> powers(3, 0)\n[]",
  "solution": "powers = lambda b, n: take(n, iterate(lambda x: x * b, 1))",
  "note": "iterate(f, 1) is 1, b, b^2, ... forever; take cuts it. O(n) multiplications.",
 },
 {
  "id": "7.4",
  "level": "drill",
  "title": "Countdown",
  "statement": "Return [n, n-1, ..., 1] with unfoldr: the seed is the current number, the unfold stops\n"
               "at zero. countdown(0) is empty.",
  "contract": "countdown(n: int) -> list[int]",
  "tests": ">>> countdown(4)\n[4, 3, 2, 1]\n>>> countdown(1)\n[1]\n>>> countdown(0)\n[]",
  "solution": "countdown = lambda n: unfoldr(lambda m: None if m == 0 else (m, m - 1), n)",
  "note": "The two-outcome contract in miniature: emit (m, m-1) or stop with None. O(n).",
 },
 {
  "id": "7.5",
  "level": "drill",
  "title": "Splice three feeds",
  "statement": "Concatenate three iterables into one list using chain -- lists, strings, anything\n"
               "iterable, in the order given.",
  "contract": "splice(a, b, c) -> list",
  "tests": ">>> splice([1], [2, 3], [])\n[1, 2, 3]\n"
           ">>> splice('ab', 'cd', 'e')\n['a', 'b', 'c', 'd', 'e']\n>>> splice([], [], [])\n[]",
  "solution": "splice = lambda a, b, c: list(chain(a, b, c))",
  "note": "chain is lazy concatenation; list() drains it. O(total length).",
 },
 {
  "id": "7.6",
  "level": "apply",
  "title": "Round-robin card deal",
  "statement": "A dealer hands cards to players in strict rotation: first card to the first player,\n"
               "second to the second, wrapping around until the cards run out. Return the (player, "
               "card)\n"
               "pairs in deal order. At least one player is guaranteed.",
  "contract": "deal(players: list[str], cards: list) -> list[tuple]",
  "tests": ">>> deal(['ann', 'bo'], [1, 2, 3, 4, 5])\n"
           "[('ann', 1), ('bo', 2), ('ann', 3), ('bo', 4), ('ann', 5)]\n"
           ">>> deal(['solo'], ['x', 'y'])\n[('solo', 'x'), ('solo', 'y')]\n"
           ">>> deal(['a', 'b'], [])\n[]",
  "solution": "deal = lambda players, cards: zip_(cycle(players), cards)",
  "note": "cycle makes the rotation infinite; zip_ stops at the shorter side -- the cards. O(cards).\n"
          "Common mistake: index arithmetic with % when cycle already says it.",
 },
 {
  "id": "7.7",
  "level": "apply",
  "title": "Colony doubling",
  "statement": "A bacteria colony starts at `start` cells and doubles every day. Return how many days\n"
               "pass before the colony first reaches at least `goal` cells (0 if it already has).\n"
               "Model the growth as an iterate stream and count the days spent below goal.",
  "contract": "days_to_reach(start: int, goal: int) -> int",
  "tests": ">>> days_to_reach(1, 8)\n3\n>>> days_to_reach(5, 5)\n0\n>>> days_to_reach(3, 100)\n6",
  "solution": "days_to_reach = lambda start, goal: len(\n"
              "    takeWhile(lambda x: x < goal, iterate(lambda x: 2 * x, start)))",
  "note": "The stream is start, 2*start, ...; the answer is how many terms stay under goal.\n"
          "O(log(goal/start)). Watch the >= boundary: day counting is off by one if you use <=.",
 },
 {
  "id": "7.8",
  "level": "apply",
  "title": "LED bit pattern",
  "statement": "An LED row shows a number in binary, most significant bit first. Return the bit list\n"
               "for n >= 1: peel bits least-significant-first with unfoldr, then reverse.",
  "contract": "bits(n: int) -> list[int]",
  "tests": ">>> bits(13)\n[1, 1, 0, 1]\n>>> bits(1)\n[1]\n>>> bits(8)\n[1, 0, 0, 0]",
  "solution": "bits = lambda n: list(reversed(unfoldr(lambda m: None if m == 0 else (m % 2, m // 2), "
              "n)))",
  "note": "unfoldr naturally emits LSB first (m % 2 peels the low bit); one reversal fixes the\n"
          "display order. O(log n).",
 },
 {
  "id": "7.9",
  "level": "apply",
  "title": "Chain of command",
  "statement": "An org chart maps each employee to their manager, with the top boss mapped to None.\n"
               "Return the chain of command from a given employee up to and including the top:\n"
               "an unfold whose seed is the current person and whose next seed is their manager.",
  "contract": "chain_of_command(boss: dict, name: str) -> list[str]",
  "tests": ">>> boss = {'amy': 'raj', 'raj': 'kim', 'kim': None}\n"
           ">>> chain_of_command(boss, 'amy')\n['amy', 'raj', 'kim']\n"
           ">>> chain_of_command(boss, 'kim')\n['kim']\n"
           ">>> chain_of_command({'x': None}, 'x')\n['x']",
  "solution": "chain_of_command = lambda boss, name: unfoldr(\n"
              "    lambda n: None if n is None else (n, boss[n]), name)",
  "note": "A parent-chain walk is an unfold: emit the person, seed becomes the manager, None stops.\n"
          "O(depth). The same shape reconstructs paths in Dijkstra.",
 },
 {
  "id": "7.10",
  "level": "apply",
  "title": "When the buses meet",
  "statement": "Bus A stops at minute a, a+da, a+2*da, ...; bus B at b, b+db, .... Return the first\n"
               "minute at or after both start times when the two schedules coincide. A shared minute\n"
               "is guaranteed to exist. Search A's infinite schedule with find.",
  "contract": "sync(a: int, da: int, b: int, db: int) -> int",
  "tests": ">>> sync(3, 4, 1, 6)\n7\n>>> sync(10, 1, 4, 7)\n11\n>>> sync(0, 5, 0, 3)\n0",
  "solution": "sync = lambda a, da, b, db: find(lambda x: x >= b and (x - b) % db == 0, count(a, da))",
  "note": "find is the only consumer that can search an infinite count stream: it stops at the\n"
          "first hit. The membership test for B's schedule is arithmetic, not a second stream.",
 },
 {
  "id": "7.11",
  "level": "challenge",
  "title": "Look-and-say",
  "statement": "The look-and-say sequence starts '1'; each term reads the previous aloud: '1' is one 1\n"
               "-> '11'; '11' is two 1s -> '21'; '21' -> '1211'; and so on. Return the nth term\n"
               "(1-indexed). Peel each term into runs of equal digits with unfoldr, encode each run as\n"
               "count then digit, and drive the whole sequence with iterate.",
  "contract": "look_and_say(n: int) -> str",
  "tests": ">>> look_and_say(1)\n'1'\n>>> look_and_say(2)\n'11'\n>>> look_and_say(3)\n'21'\n"
           ">>> look_and_say(5)\n'111221'",
  "solution": "def look_and_say(n):\n"
              "    def peel(u):\n"
              "        if u == \"\":\n"
              "            return None\n"
              "        i = fromMaybe(len(u), find(lambda j: u[j] != u[0], range(1, len(u))))\n"
              "        return (u[:i], u[i:])\n"
              "    step = lambda s: \"\".join(map_(lambda r: str(len(r)) + r[0], unfoldr(peel, s)))\n"
              "    return take(n, iterate(step, \"1\"))[-1]",
  "note": "Two unfolds stacked: unfoldr peels one term into runs (find locates where the run ends,\n"
          "fromMaybe handles the final run), and iterate unfolds the sequence of terms. O(n * term\n"
          "length). Common mistake: forgetting the last run when no differing digit exists.",
 },
 {
  "id": "7.12",
  "level": "challenge",
  "title": "Hailstone champion",
  "statement": "The hailstone (Collatz) trajectory of n repeatedly halves even numbers and maps odd m\n"
               "to 3*m + 1, ending at 1. Among all starts 1..limit, return the start with the LONGEST\n"
               "trajectory (counting every term including the final 1); ties go to the smaller start.\n"
               "Express one trajectory as an unfoldr and measure it.",
  "contract": "hail_champion(limit: int) -> int",
  "tests": ">>> hail_champion(1)\n1\n>>> hail_champion(10)\n9\n>>> hail_champion(30)\n27",
  "solution": "def hail_champion(limit):\n"
              "    step = lambda m: None if m == 1 else (m, m // 2 if even(m) else 3 * m + 1)\n"
              "    length = lambda n: len(unfoldr(step, n)) + 1\n"
              "    return max(range(1, limit + 1), key=length)",
  "note": "unfoldr emits every term before 1, so trajectory length is len + 1. max with key= keeps\n"
          "the FIRST winner on ties, and range ascends, so ties resolve to the smaller start for\n"
          "free. Interview follow-up: memoize lengths across starts with memo.",
 },
]
