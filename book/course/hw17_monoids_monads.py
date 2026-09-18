CHAPTER = 17
TITLE = "Monoids and Monads"

ITEMS = [
{
 "id": "17.1", "level": "drill", "title": "An XOR monoid",
 "statement": "Build a Monoid pairing False (the identity) with XOR as the combining op, then use\n"
              "mconcat to fold a whole list of bools through it. XOR toggles a bit once per True.",
 "contract": "xor_all(bits: list[bool]) -> bool",
 "tests": ">>> xor_all([True, False, True])\nFalse\n>>> xor_all([True])\nTrue\n"
          ">>> xor_all([True, True])\nFalse\n>>> xor_all([])\nFalse",
 "solution": "XorM = Monoid(False, lambda a, b: a != b)\n"
             "xor_all = lambda bits: mconcat(XorM, bits)",
 "note": "Naming the pair is the whole trick: once XOR is a monoid, mconcat is the fold engine for "
         "free. The identity False is why the empty list answers False, not an error.",
},
{
 "id": "17.2", "level": "drill", "title": "Total length via foldMap",
 "statement": "Use foldMap with the Sum monoid to add up the lengths of a list of strings. foldMap\n"
              "maps each element into the monoid (here, its length) and then mconcats the results.",
 "contract": "total_length(words: list[str]) -> int",
 "tests": ">>> total_length(['ab', 'c', ''])\n3\n>>> total_length([])\n0\n"
          ">>> total_length(['hello', 'world'])\n10",
 "solution": "total_length = lambda words: foldMap(len, Sum, words)",
 "note": "foldMap(f, m, xs) is 'measure, then combine': len is the measure, Sum's (0, add) is the "
         "combiner. Most monoid use in practice is foldMap use, not a bare mconcat.",
},
{
 "id": "17.3", "level": "drill", "title": "Factorial via Product",
 "statement": "Use mconcat with the Product monoid over range(1, n + 1) to compute n!. Product's\n"
              "identity is 1, so the empty product (n == 0) comes out right with no special case.",
 "contract": "factorial(n: int) -> int",
 "tests": ">>> factorial(5)\n120\n>>> factorial(0)\n1\n>>> factorial(1)\n1\n>>> factorial(4)\n24",
 "solution": "factorial = lambda n: mconcat(Product, range(1, n + 1))",
 "note": "Product's identity 1 is what makes the n == 0 case (an empty range) a lawful factorial "
         "instead of a special-cased branch -- that is the whole point of an identity element.",
},
{
 "id": "17.4", "level": "apply", "title": "Max and min in one pass",
 "statement": "Use both(MaxM, MinM) to build a monoid that tracks the running maximum AND minimum\n"
              "together, then mconcat a list of (x, x) pairs through it -- one pass, two answers.",
 "contract": "max_min(xs: list[int]) -> tuple[int, int]",
 "tests": ">>> max_min([3, 1, 4, 1, 5])\n(5, 1)\n>>> max_min([7])\n(7, 7)\n"
          ">>> max_min([2, 9, 4, 9, 2])\n(9, 2)",
 "solution": "MaxMin = both(MaxM, MinM)\n"
             "max_min = lambda xs: mconcat(MaxMin, [(x, x) for x in xs])",
 "note": "both pairs two monoids into one over pairs: the tuple monoid's op runs each side's op on "
         "its own half. Chain both again for a third statistic in the same single pass.",
},
{
 "id": "17.5", "level": "apply", "title": "Safe square-root-then-reciprocal",
 "statement": "Chain two None-propagating steps with chainM: first take a square root (only for\n"
              "n >= 0), then a reciprocal (only if the result is nonzero). chainM runs its LEFTMOST\n"
              "function first, and bind stops the whole chain the moment a step returns None.",
 "contract": "safe_pipeline(n: float) -> float | None",
 "tests": ">>> safe_pipeline(4)\n0.5\n>>> safe_pipeline(-1) is None\nTrue\n"
          ">>> safe_pipeline(0) is None\nTrue\n>>> safe_pipeline(16)\n0.25",
 "solution": "sqrt_step = lambda n: n ** 0.5 if n >= 0 else None\n"
             "recip_step = lambda n: 1 / n if n != 0 else None\n"
             "safe_pipeline = chainM(sqrt_step, recip_step)",
 "note": "chainM(*fs) folds bind over the steps left to right -- the OPPOSITE order from compose. "
         "None from either step poisons everything after it without an if-ladder.",
},
{
 "id": "17.6", "level": "apply", "title": "Parse every entry, or fail entirely",
 "statement": "Use traverseM to parse a list of strings as integers, demanding EVERY entry succeed.\n"
              "A single unparseable entry should make the whole result None -- all-or-nothing, like\n"
              "sequenceM but with the parse step folded in.",
 "contract": "parse_all(strs: list[str]) -> list[int] | None",
 "tests": ">>> parse_all(['1', '2', '3'])\n[1, 2, 3]\n>>> parse_all(['1', 'x', '3']) is None\nTrue\n"
          ">>> parse_all([])\n[]\n>>> parse_all(['-5', '7'])\n[-5, 7]",
 "solution": "parse_one = lambda s: int(s) if s.lstrip('-').isdigit() else None\n"
             "parse_all = lambda strs: traverseM(parse_one, strs)",
 "note": "traverseM(f, xs) is sequenceM(map_(f, xs)) fused into one call: map a failable step, then "
         "demand every success. The empty list traverses to [], vacuously all-or-nothing.",
},
{
 "id": "17.7", "level": "challenge", "title": "Validate an age, keeping the reason",
 "statement": "Where Maybe only says 'it failed', Either says WHY. Write two Ok/Err-returning steps --\n"
              "parse a digit string, then range-check it -- and chain them with chainE. chainE's first\n"
              "step still takes the raw value; only the WIRING between steps is Ok/Err-aware.",
 "contract": "validate_age(raw: str) -> tuple",
 "tests": ">>> validate_age('42')\n('ok', 42)\n>>> validate_age('abc')\n('err', 'not a number')\n"
          ">>> validate_age('200')\n('err', 'out of range')\n>>> validate_age('0')\n('ok', 0)",
 "solution": "parse_step = lambda s: Ok(int(s)) if s.isdigit() else Err('not a number')\n"
             "range_step = lambda n: Ok(n) if 0 <= n <= 150 else Err('out of range')\n"
             "validate_age = chainE(parse_step, range_step)",
 "note": "bindE short-circuits on the first Err but keeps its message, unlike bind's bare None. "
         "chainE(*fs) is exactly chainM's shape, generalised from 'failed or not' to 'failed, why'.",
},
{
 "id": "17.8", "level": "challenge", "title": "Validate a whole roster",
 "statement": "Hand-roll a sequenceE by folding bindE over a list, reusing a per-entry validator like\n"
              "17.7's: collect every valid age into one Ok list, or stop at the first Err and report\n"
              "it. The accumulator threads an Either the way sequenceM threads a Maybe.",
 "contract": "validate_roster(raws: list[str]) -> tuple",
 "tests": ">>> validate_roster(['10', '20', '30'])\n('ok', [10, 20, 30])\n"
          ">>> validate_roster(['10', 'abc', '30'])\n('err', 'not a number')\n"
          ">>> validate_roster(['10', '200'])\n('err', 'out of range')\n"
          ">>> validate_roster([])\n('ok', [])",
 "solution": "parse_step = lambda s: Ok(int(s)) if s.isdigit() else Err('not a number')\n"
             "range_step = lambda n: Ok(n) if 0 <= n <= 150 else Err('out of range')\n"
             "validate_age = chainE(parse_step, range_step)\n"
             "def step(acc, raw):\n"
             "    return bindE(acc, lambda xs: bindE(validate_age(raw), lambda v: Ok(xs + [v])))\n"
             "validate_roster = lambda raws: foldl(step, raws, Ok([]))",
 "note": "Ok([]) seeds the fold the way [] seeds sequenceM; each step's bindE only advances the "
         "accumulator when both the prior entries and this one are Ok. First Err wins and sticks.",
},
]
