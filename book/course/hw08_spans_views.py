CHAPTER = 8
TITLE = "Spans and Views"

ITEMS = [
 {
  "id": "8.1",
  "level": "drill",
  "title": "Leading run",
  "statement": "Return the longest prefix of xs whose elements are all strictly positive, using span.\n"
               "The rest of the list is discarded.",
  "contract": "leading_positive(xs: list) -> list",
  "tests": ">>> leading_positive([2, 5, 1, -1, 9])\n[2, 5, 1]\n"
           ">>> leading_positive([-1, 2])\n[]\n>>> leading_positive([4, 4])\n[4, 4]",
  "solution": "leading_positive = lambda xs: span(lambda x: x > 0, xs)[0]",
  "note": "span returns (prefix, rest) in one pass; take the first component. O(prefix length).",
 },
 {
  "id": "8.2",
  "level": "drill",
  "title": "Peek first k",
  "statement": "Return the first k elements of a possibly-infinite stream with take. If the stream is\n"
               "shorter than k, return all of it -- take never complains.",
  "contract": "peek(k: int, xs) -> list",
  "tests": ">>> peek(3, count(0))\n[0, 1, 2]\n>>> peek(5, [1, 2])\n[1, 2]\n>>> peek(0, count(9))\n[]",
  "solution": "peek = lambda k, xs: take(k, xs)",
  "note": "take is the safe window onto an infinite stream; islice underlies it. O(k).",
 },
 {
  "id": "8.3",
  "level": "drill",
  "title": "Skip the header",
  "statement": "A list begins with comment lines starting '#'. Drop that leading block and return the\n"
               "remaining lines, using dropWhile. Once a non-comment line appears, keep everything.",
  "contract": "skip_header(lines: list) -> list",
  "tests": ">>> skip_header(['# a', '# b', 'x', '# c'])\n['x', '# c']\n"
           ">>> skip_header(['data'])\n['data']\n>>> skip_header(['# only'])\n[]",
  "solution": "skip_header = lambda lines: dropWhile(lambda s: s.startswith('#'), lines)",
  "note": "dropWhile discards while true, then keeps the rest untested -- note '# c' survives.\n"
          "O(n).",
 },
 {
  "id": "8.4",
  "level": "drill",
  "title": "Every prefix",
  "statement": "Return every prefix of xs from empty to the whole list, using inits.",
  "contract": "prefixes(xs: list) -> list[list]",
  "tests": ">>> prefixes([1, 2, 3])\n[[], [1], [1, 2], [1, 2, 3]]\n"
           ">>> prefixes([])\n[[]]\n>>> prefixes(['a'])\n[[], ['a']]",
  "solution": "prefixes = lambda xs: inits(xs)",
  "note": "inits gives len(xs)+1 prefixes, empty first. O(n^2) total size.",
 },
 {
  "id": "8.5",
  "level": "drill",
  "title": "Deal into pages",
  "statement": "Split a list into consecutive pages of size k; the final page may be short. Use "
               "chunksOf.",
  "contract": "paginate(k: int, xs: list) -> list[list]",
  "tests": ">>> paginate(2, [1, 2, 3, 4, 5])\n[[1, 2], [3, 4], [5]]\n"
           ">>> paginate(3, [1, 2, 3])\n[[1, 2, 3]]\n>>> paginate(2, [])\n[]",
  "solution": "paginate = lambda k, xs: chunksOf(k, xs)",
  "note": "chunksOf is pure slicing, so it works on lists and strings alike. O(n).",
 },
 {
  "id": "8.6",
  "level": "apply",
  "title": "Read the leading integer",
  "statement": "A token string begins with an optional run of digits, then arbitrary characters. "
               "Return\n"
               "the leading integer, or 0 if no digit starts it. Use span to split the digit run from\n"
               "the tail, then interpret it.",
  "contract": "read_int(s: str) -> int",
  "tests": ">>> read_int('123abc')\n123\n>>> read_int('7')\n7\n>>> read_int('abc')\n0\n>>> "
           "read_int('')\n0",
  "solution": "read_int = lambda s: int(\"\".join(span(str.isdigit, s)[0]) or \"0\")",
  "note": "span(str.isdigit, s)[0] is the digit prefix as a char list; join and int it, with 'or 0'\n"
          "for the empty case. This is exactly how a lexer peels one token. O(len).",
 },
 {
  "id": "8.7",
  "level": "apply",
  "title": "Split on the first blank",
  "statement": "An email is a header block followed by a blank line ('') and then the body. Return\n"
               "(headers, body) where headers excludes the blank separator and body is the lines after\n"
               "it. Use break_ to cut at the first blank line. If there is no blank line, the body is\n"
               "empty.",
  "contract": "split_email(lines: list) -> tuple",
  "tests": ">>> split_email(['To: a', 'Re: b', '', 'hello', 'bye'])\n"
           "(['To: a', 'Re: b'], ['hello', 'bye'])\n"
           ">>> split_email(['To: a', 'Re: b'])\n(['To: a', 'Re: b'], [])\n"
           ">>> split_email(['', 'body'])\n([], ['body'])",
  "solution": "def split_email(lines):\n"
              "    head, rest = break_(lambda s: s == '', lines)\n"
              "    return (head, rest[1:])",
  "note": "break_ splits at the first line where the predicate holds -- the blank -- putting it at\n"
          "the front of rest, so rest[1:] drops the separator. O(n).",
 },
 {
  "id": "8.8",
  "level": "apply",
  "title": "Read up to the sentinel",
  "statement": "A sensor emits readings terminated by a sentinel value -1. Return the readings up to "
               "AND\n"
               "including the first -1 (the do-while flavour: the terminator is part of the record).\n"
               "Use takeuntil. If no -1 appears, return the whole list.",
  "contract": "read_record(xs: list) -> list",
  "tests": ">>> read_record([4, 7, -1, 9])\n[4, 7, -1]\n"
           ">>> read_record([1, 2, 3])\n[1, 2, 3]\n>>> read_record([-1, 5])\n[-1]",
  "solution": "read_record = lambda xs: list(takeuntil(lambda x: x == -1, xs))",
  "note": "takeuntil INCLUDES the first hit, unlike takewhile which would stop just before -1.\n"
          "O(record length). Common mistake: using takewhile and losing the sentinel.",
 },
 {
  "id": "8.9",
  "level": "apply",
  "title": "Longest good prefix length",
  "statement": "Given a list of daily temperatures, a warm streak from day 0 runs while each day is at\n"
               "least `floor`. Return how many opening days form that streak, using span to isolate "
               "the\n"
               "prefix and measuring it. A first day below floor gives 0.",
  "contract": "warm_streak(temps: list, floor: int) -> int",
  "tests": ">>> warm_streak([70, 72, 68, 90], 70)\n2\n"
           ">>> warm_streak([60, 80], 70)\n0\n>>> warm_streak([75, 75, 75], 70)\n3",
  "solution": "warm_streak = lambda temps, floor: len(span(lambda t: t >= floor, temps)[0])",
  "note": "span isolates the leading run, len measures it -- one pass, no manual counter. O(streak).",
 },
 {
  "id": "8.10",
  "level": "apply",
  "title": "All substrings",
  "statement": "Return every non-empty contiguous substring of s, in the order: by start position, "
               "then\n"
               "by length. The tool is tails -- every substring is a non-empty prefix of some suffix.\n"
               "So take each suffix's inits, drop the empty one, and concatenate.",
  "contract": "substrings(s: str) -> list[str]",
  "tests": ">>> substrings('ab')\n['a', 'ab', 'b']\n"
           ">>> substrings('a')\n['a']\n>>> substrings('')\n[]\n"
           ">>> substrings('xyz')\n['x', 'xy', 'xyz', 'y', 'yz', 'z']",
  "solution": "substrings = lambda s: concatMap(\n"
              "    lambda suf: map_(lambda p: \"\".join(p), inits(list(suf))[1:]),\n"
              "    takeWhile(lambda suf: suf != \"\", tails(s)))",
  "note": "tails gives every suffix (dropping the empty tail); each suffix's inits[1:] are its\n"
          "non-empty prefixes -- together, every substring. O(n^2) substrings, the true size.",
 },
 {
  "id": "8.11",
  "level": "challenge",
  "title": "Run-length split",
  "statement": "Split a list into maximal runs of equal consecutive elements, WITHOUT using group or\n"
               "groupBy -- do it directly with span. Peel the leading run (all elements equal to the\n"
               "head) off the front repeatedly until the list is empty.",
  "contract": "runs(xs: list) -> list[list]",
  "tests": ">>> runs([1, 1, 2, 3, 3, 3])\n[[1, 1], [2], [3, 3, 3]]\n"
           ">>> runs([])\n[]\n>>> runs(['a'])\n[['a']]\n"
           ">>> runs([5, 5, 5])\n[[5, 5, 5]]",
  "solution": "def runs(xs):\n"
              "    peel = lambda ys: None if ys == [] else span(lambda x: x == ys[0], ys)\n"
              "    return unfoldr(peel, list(xs))",
  "note": "span(equal-to-head) is exactly one run; unfoldr repeats the peel until empty. This is how\n"
          "group is built. O(n). Common mistake: comparing to the previous element instead of the\n"
          "run's head.",
 },
 {
  "id": "8.12",
  "level": "challenge",
  "title": "Justify to width",
  "statement": "Greedily wrap words into lines no longer than `width` characters, words joined by "
               "single\n"
               "spaces; each line packs as many words as fit. Every word is guaranteed to fit alone.\n"
               "Peel one line at a time: take the longest prefix of the remaining words whose joined\n"
               "length stays within width, emit it, continue with the rest.",
  "contract": "justify(words: list, width: int) -> list[str]",
  "tests": ">>> justify(['a', 'bb', 'ccc'], 6)\n['a bb', 'ccc']\n"
           ">>> justify(['one', 'two', 'three'], 7)\n['one two', 'three']\n"
           ">>> justify([], 5)\n[]\n"
           ">>> justify(['hello'], 5)\n['hello']",
  "solution": "def justify(words, width):\n"
              "    def peel(ws):\n"
              "        if ws == []:\n"
              "            return None\n"
              "        fits = lambda k: len(unwords(ws[:k])) <= width\n"
              "        k = last(takeWhile(fits, range(1, len(ws) + 1)))\n"
              "        return (unwords(ws[:k]), ws[k:])\n"
              "    return unfoldr(peel, list(words))",
  "note": "unfoldr peels one line per step; takeWhile(fits, count(1)) finds the largest word count\n"
          "that fits, and last takes it. O(total characters). Every word fitting alone guarantees\n"
          "k >= 1, so the unfold always makes progress.",
 },
]
