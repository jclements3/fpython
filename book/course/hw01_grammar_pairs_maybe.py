CHAPTER = 1
TITLE = "Grammar, Pairs and Maybe"

ITEMS = [
{
 "id": "1.1", "level": "drill", "title": "Mirror a pair",
 "statement": "Write mirror(p): the pair with its elements exchanged. Applying it twice must give the\n"
              "original pair back.",
 "contract": "mirror(p) -> pair",
 "tests": ">>> mirror((1, 2))\n(2, 1)\n>>> mirror(('lo', 'hi'))\n('hi', 'lo')\n"
          ">>> mirror(mirror((3, 4)))\n(3, 4)",
 "solution": "mirror = swap",
 "note": "Recognize-it drill: mirror IS swap. Involution property (twice = identity) is worth saying.",
},
{
 "id": "1.2", "level": "drill", "title": "Record projections",
 "statement": "A leaderboard record is a (name, score) pair. Write name_of(r) and score_of(r) using "
              "the\n"
              "pair accessors, not indexing.",
 "contract": "name_of(r) -> value; score_of(r) -> value",
 "tests": ">>> r = ('ada', 95)\n>>> name_of(r)\n'ada'\n>>> score_of(r)\n95\n"
          ">>> name_of(swap(r))\n95",
 "solution": "name_of = fst\nscore_of = snd",
 "note": "fst/snd read better than [0]/[1] in pair-heavy code and slot into higher-order positions.",
},
{
 "id": "1.3", "level": "drill", "title": "Default when missing",
 "statement": "Write or_default(d, x): x itself unless x is None, in which case d. Falsy values like 0\n"
              "and '' are real data and must survive.",
 "contract": "or_default(d, x) -> value",
 "tests": ">>> or_default(0, None)\n0\n>>> or_default(0, 5)\n5\n>>> or_default(9, 0)\n0\n"
          ">>> or_default('-', None)\n'-'",
 "solution": "or_default = fromMaybe",
 "note": "fromMaybe verbatim. The teaching point is the third test: only None triggers the default,\n"
         "unlike `x or d` which would destroy the 0.",
},
{
 "id": "1.4", "level": "drill", "title": "The sentinel argument",
 "statement": "Write greet(name=NOTHING) returning 'hello, stranger' when NO argument was passed, and\n"
              "'hello, ' + str(name) otherwise -- including when the caller passes None on purpose.",
 "contract": "greet(name=NOTHING) -> str",
 "tests": ">>> greet()\n'hello, stranger'\n>>> greet('ada')\n'hello, ada'\n"
          ">>> greet(None)\n'hello, None'",
 "solution": "def greet(name=NOTHING):\n"
             "    return 'hello, stranger' if name is NOTHING else 'hello, ' + str(name)",
 "note": "NOTHING distinguishes omitted from None-as-data; test with `is`. A None default could not\n"
         "pass the third doctest.",
},
{
 "id": "1.5", "level": "drill", "title": "Manufactured defaults",
 "statement": "Write make_default(v): a function that returns a one-argument function answering v no\n"
              "matter what it is asked.",
 "contract": "make_default(v) -> function",
 "tests": ">>> make_default(7)('anything')\n7\n>>> f = make_default(0)\n>>> f(99)\n0\n"
          ">>> f('x')\n0",
 "solution": "make_default = const",
 "note": "const verbatim -- the constant function factory that fills callback slots.",
},
{
 "id": "1.6", "level": "apply", "title": "Leaderboard by name",
 "statement": "The scoring service emits (score, name) pairs, but the display wants (name, score).\n"
              "Write by_name(pairs) converting the whole list, order preserved.",
 "contract": "by_name(pairs) -> list of pairs",
 "tests": ">>> by_name([(95, 'ada'), (87, 'bob')])\n[('ada', 95), ('bob', 87)]\n"
          ">>> by_name([])\n[]\n>>> by_name([(1, 'solo')])\n[('solo', 1)]",
 "solution": "by_name = lambda ps: [swap(p) for p in ps]",
 "note": "swap mapped over the list. O(n); the common slip is reversing the list instead of each pair.",
},
{
 "id": "1.7", "level": "apply", "title": "Config with fallbacks",
 "statement": "Settings live in a dict; an absent key means 'use the default'. Write\n"
              "setting(cfg, key, default). A stored falsy value (False, 0, '') is a deliberate choice\n"
              "and must be returned as-is.",
 "contract": "setting(cfg, key, default) -> value",
 "tests": ">>> setting({'retries': 3}, 'retries', 1)\n3\n>>> setting({}, 'retries', 1)\n1\n"
          ">>> setting({'debug': False}, 'debug', True)\nFalse",
 "solution": "setting = lambda cfg, key, default: fromMaybe(default, cfg.get(key))",
 "note": "dict.get is already a None-returning lookup, so fromMaybe finishes it. `cfg.get(key) or\n"
         "default` would fail the False test.",
},
{
 "id": "1.8", "level": "apply", "title": "Invert the phone book",
 "statement": "A phone book maps names to numbers, and numbers are unique. Produce the reverse index\n"
              "mapping each number back to its name.",
 "contract": "invert_book(d) -> dict",
 "tests": ">>> invert_book({'ada': '555-01', 'bob': '555-02'})\n"
          "{'555-01': 'ada', '555-02': 'bob'}\n>>> invert_book({})\n{}\n"
          ">>> invert_book({'x': 1})\n{1: 'x'}",
 "solution": "invert_book = lambda d: dict(swap(kv) for kv in d.items())",
 "note": "A dict is a list of pairs wearing a hat: items, swap each, dict. Uniqueness of values is\n"
         "what makes the inversion lossless.",
},
{
 "id": "1.9", "level": "apply", "title": "First good sensor fix",
 "statement": "A sensor log is a list of (timestamp, reading) pairs where a failed sample records\n"
              "None. Return the first non-None reading, or the supplied default when every sample\n"
              "failed (or the log is empty). A reading of 0 is a real fix.",
 "contract": "first_fix(default, log) -> value",
 "tests": ">>> first_fix(-1, [(1, None), (2, 7.5), (3, 8.0)])\n7.5\n"
          ">>> first_fix(-1, [(1, None), (2, None)])\n-1\n>>> first_fix(-1, [])\n-1\n"
          ">>> first_fix(-1, [(1, 0)])\n0",
 "solution": "first_fix = lambda default, log: fromMaybe(\n"
             "    default, find(isJust, map(snd, log)))",
 "note": "Reshape then search: bare map keeps the scan lazy, find(isJust, ...) stops at the first real\n"
         "reading, fromMaybe lands the caller's default. The zero test is the None-vs-falsy discipline\n"
         "again -- isJust asks identity against None, never truthiness.",
},
{
 "id": "1.10", "level": "apply", "title": "Effective badge ids",
 "statement": "Each visitor holds (badge_or_None, temp_id). The effective id is the badge when one was\n"
              "issued, else the temp id. Map a whole visitor list to effective ids; an empty-string\n"
              "badge is a real (blank) badge, not a missing one.",
 "contract": "effective_ids(pairs) -> list",
 "tests": ">>> effective_ids([(None, 'T1'), ('B2', 'T2'), (None, 'T3')])\n['T1', 'B2', 'T3']\n"
          ">>> effective_ids([])\n[]\n>>> effective_ids([('', 'T9')])\n['']",
 "solution": "effective_ids = lambda ps: [fromMaybe(snd(p), fst(p)) for p in ps]",
 "note": "fromMaybe per element with the pair accessors supplying both sides. `badge or temp` would\n"
         "fail the blank-badge test.",
},
{
 "id": "1.11", "level": "challenge", "title": "Ledger reconciliation",
 "statement": "Ledger rows are (txn_id, debit_or_None, credit_or_None); a None side simply was not\n"
              "recorded and counts as 0 toward the balance. Return the pair (net, incomplete): net is\n"
              "total credits minus total debits; incomplete counts rows where EITHER side is missing.",
 "contract": "reconcile(rows) -> (net, incomplete)",
 "tests": ">>> reconcile([('a', 5, None), ('b', None, 10), ('c', 2, 3)])\n(6, 2)\n"
          ">>> reconcile([])\n(0, 0)\n>>> reconcile([('x', 1, 4)])\n(3, 0)\n"
          ">>> reconcile([('y', None, None)])\n(0, 1)",
 "solution": "def reconcile(rows):\n"
             "    net = sum(fromMaybe(0, r[2]) - fromMaybe(0, r[1]) for r in rows)\n"
             "    incomplete = sum(1 for r in rows if r[1] is None or r[2] is None)\n"
             "    return (net, incomplete)",
 "note": "Two passes, each a one-liner: fromMaybe turns absence into the additive identity; the\n"
         "incomplete count keeps the audit trail honest. O(n).",
},
{
 "id": "1.12", "level": "challenge", "title": "Three-level settings cascade",
 "statement": "Configuration resolves through a cascade: an environment dict overrides a config-file\n"
              "dict, which overrides a built-in default. Absence at a level means None from .get;\n"
              "stored falsy values win like any other value. Write resolve(key, env, cfg, default).",
 "contract": "resolve(key, env, cfg, default) -> value",
 "tests": ">>> resolve('p', {'p': 1}, {'p': 2}, 9)\n1\n>>> resolve('p', {}, {'p': 2}, 9)\n2\n"
          ">>> resolve('p', {}, {}, 9)\n9\n>>> resolve('debug', {}, {'debug': 0}, 1)\n0",
 "solution": "resolve = lambda key, env, cfg, default: fromMaybe(\n"
             "    fromMaybe(default, cfg.get(key)), env.get(key))",
 "note": "fromMaybe NESTS: the inner call resolves cfg-vs-default, and that result becomes the outer\n"
         "default for env. Reading it inside-out is the exercise.",
},
]
