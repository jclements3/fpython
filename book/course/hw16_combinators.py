CHAPTER = 16
TITLE = "Combinators Capstone"

ITEMS = [
{
 "id": "16.1", "level": "drill", "title": "Compose three",
 "statement": "Use compose to build a single function that strips a string, lowercases it, then\n"
              "reverses it -- in that order of effect. Remember compose runs its RIGHTMOST function\n"
              "first, so the last stage you write is the first that happens.",
 "contract": "clean_reverse: str -> str",
 "tests": ">>> clean_reverse('  Hello  ')\n'olleh'\n>>> clean_reverse('ABC')\n'cba'\n"
          ">>> clean_reverse('')\n''",
 "solution": "clean_reverse = compose(lambda s: s[::-1], str.lower, str.strip)",
 "note": "compose(f, g, h)(x) == f(g(h(x))): strip happens first because it is rightmost. "
         "Point-free: no lambda parameter of your own.",
},
{
 "id": "16.2", "level": "drill", "title": "Flip subtract",
 "statement": "Given the two-argument function sub(a, b) = a - b, use flip to make a function that\n"
              "subtracts the FIRST argument from the second. flip swaps argument order and nothing "
              "else.",
 "contract": "rsub: (int, int) -> int   (rsub(a, b) == b - a)",
 "tests": ">>> rsub(1, 10)\n9\n>>> rsub(10, 1)\n-9\n>>> rsub(5, 5)\n0",
 "solution": "sub = lambda a, b: a - b\n"
             "rsub = flip(sub)",
 "note": "flip is a pure adapter -- it computes nothing, just reorders. This is exactly how the "
         "prelude derives foldr from foldl.",
},
{
 "id": "16.3", "level": "drill", "title": "Add via curry",
 "statement": "Curry the function add(a, b) = a + b, then use the curried form to build add_ten, a\n"
              "one-argument function that adds 10. Show that binding the first argument yields a\n"
              "reusable function.",
 "contract": "add_ten: int -> int",
 "tests": ">>> add_ten(5)\n15\n>>> add_ten(-10)\n0\n>>> add_ten(0)\n10",
 "solution": "add = lambda a, b: a + b\n"
             "add_ten = curry(add)(10)",
 "note": "curry(add)(10) captures 10 in a closure and returns a function still waiting for the "
         "second argument. That half-applied function is a value you can name.",
},
{
 "id": "16.4", "level": "drill", "title": "Constant column",
 "statement": "Use const and map_ to replace every element of a list with the string 'x', regardless\n"
              "of its value. const(v) is the function that ignores its argument and always answers v.",
 "contract": "mask(xs: list) -> list[str]",
 "tests": ">>> mask([1, 2, 3])\n['x', 'x', 'x']\n>>> mask([])\n[]\n>>> mask(['a', None, 7])\n['x', 'x', "
          "'x']",
 "solution": "mask = lambda xs: map_(const('x'), xs)",
 "note": "const fills a callback slot with a constant. Reaching for a lambda z: 'x' would work too, "
         "but const names the intent.",
},
{
 "id": "16.5", "level": "drill", "title": "Partial power",
 "statement": "Use partial to freeze the base of pow, producing powers_of_two(exp) == 2 ** exp.\n"
              "partial(f, *leading) fixes the first arguments now and takes the rest later.",
 "contract": "powers_of_two: int -> int",
 "tests": ">>> powers_of_two(0)\n1\n>>> powers_of_two(10)\n1024\n>>> powers_of_two(5)\n32",
 "solution": "powers_of_two = partial(pow, 2)",
 "note": "partial binds any number of leading args in one shot; curry binds them one call at a time. "
         "Here one frozen base is all we need.",
},
{
 "id": "16.6", "level": "apply", "title": "Sort records by a field",
 "statement": "You have (name, age) tuples. Sort them oldest-first, using on to build the comparator\n"
              "from a plain numeric compare and the snd accessor, fed through sortBy. on(f, key)(x, y)\n"
              "routes BOTH arguments through key before f.",
 "contract": "by_age_desc(people: list[tuple]) -> list[tuple]",
 "tests": ">>> by_age_desc([('ada', 36), ('bob', 41), ('cy', 19)])\n"
          "[('bob', 41), ('ada', 36), ('cy', 19)]\n"
          ">>> by_age_desc([])\n[]\n>>> by_age_desc([('x', 5)])\n[('x', 5)]",
 "solution": "by_age_desc = lambda people: sortBy(on(lambda a, b: b - a, snd), people)",
 "note": "on separates the projection (snd) from the comparison (b - a for descending). This is "
         "Haskell's `comparing` idiom; a per-element key with sortOn would also work here.",
},
{
 "id": "16.7", "level": "apply", "title": "Traffic-light rules table",
 "statement": "Classify an integer as 'neg', 'zero', or 'pos' using a RULES table: a list of\n"
              "(predicate, result) pairs tried in order, with find picking the first match. The\n"
              "catch-all arm is const(otherwise) -- since table guards are APPLIED to the value, the\n"
              "always-true guard must itself be a function of the value.",
 "contract": "classify(n: int) -> str",
 "tests": ">>> classify(-4)\n'neg'\n>>> classify(0)\n'zero'\n>>> classify(9)\n'pos'\n"
          ">>> map_(classify, [-1, 0, 1])\n['neg', 'zero', 'pos']",
 "solution": "RULES = [(lambda n: n < 0, const('neg')),\n"
             "         (lambda n: n == 0, const('zero')),\n"
             "         (const(otherwise), const('pos'))]\n"
             "classify = lambda n: snd(find(lambda rule: fst(rule)(n), RULES))(n)",
 "note": "An if/elif ladder rewritten as data: rules become appendable and testable in isolation. "
         "const(otherwise) is the always-true arm; a bare True would crash when applied.",
},
{
 "id": "16.8", "level": "apply", "title": "Pipeline from a list of steps",
 "statement": "Given a list of one-argument functions, build a single function that runs them\n"
              "left-to-right (first in the list runs first) and apply it to x. Note this is the\n"
              "OPPOSITE order from compose, so reverse before composing.",
 "contract": "pipe(steps: list, x)",
 "tests": ">>> pipe([lambda a: a + 1, lambda a: a * 2], 5)\n12\n"
          ">>> pipe([], 7)\n7\n>>> pipe([str.strip, str.upper], '  hi ')\n'HI'",
 "solution": "pipe = lambda steps, x: compose(*reversed(steps))(x)",
 "note": "compose is right-to-left; a left-to-right pipeline just reverses the list first. The "
         "empty pipeline is the identity, which compose() already gives you.",
},
{
 "id": "16.9", "level": "apply", "title": "Group-and-count, point-free key",
 "statement": "Count how many words fall into each length bucket. Build the (key, value) pairs with\n"
              "the length as key and 1 as value, then fold them into a dict with fromListWith and\n"
              "addition. Use partial or a small helper to make the pair-builder read cleanly.",
 "contract": "length_histogram(words: list[str]) -> dict[int, int]",
 "tests": ">>> length_histogram(['a', 'bb', 'cc', 'ddd'])\n{1: 1, 2: 2, 3: 1}\n"
          ">>> length_histogram([])\n{}\n>>> length_histogram(['x', 'y', 'z'])\n{1: 3}",
 "solution": "pair = lambda w: (len(w), 1)\n"
             "length_histogram = lambda words: fromListWith(lambda new, old: new + old,\n"
             "                                              map_(pair, words))",
 "note": "fromListWith is the dict-building fold; addition is commutative so the new/old order is "
         "irrelevant here. O(n).",
},
{
 "id": "16.10", "level": "apply", "title": "Equality up to a key",
 "statement": "Write same_by(key, a, b): true when a and b are equal AFTER passing through key. Build\n"
              "it with on so the projection lives in one place. Then a doctest shows it grouping\n"
              "case-insensitively.",
 "contract": "same_by(key, a, b) -> bool",
 "tests": ">>> same_by(str.lower, 'ABC', 'abc')\nTrue\n>>> same_by(len, 'ab', 'cd')\nTrue\n"
          ">>> same_by(len, 'ab', 'c')\nFalse\n>>> groupBy(partial(same_by, str.lower), ['a', 'A', "
          "'b'])\n"
          "[['a', 'A'], ['b']]",
 "solution": "same_by = lambda key, a, b: on(lambda x, y: x == y, key)(a, b)",
 "note": "on(eq, key) is the reusable 'equal through a projection'. partial(same_by, str.lower) then "
         "feeds groupBy a two-argument equivalence -- combinators composing with the containers.",
},
{
 "id": "16.11", "level": "challenge", "title": "Compose a validation pipeline",
 "statement": "Each validator is a function that returns None on success or an error string on "
              "failure.\n"
              "Run a list of validators over a value and return the FIRST error, or None if all pass.\n"
              "Build the check with map_ and find; a value passes when find turns up no error.",
 "contract": "first_error(validators: list, x)",
 "tests": ">>> pos = lambda n: None if n > 0 else 'not positive'\n"
          ">>> even_v = lambda n: None if n % 2 == 0 else 'not even'\n"
          ">>> first_error([pos, even_v], 4) is None\nTrue\n"
          ">>> first_error([pos, even_v], -3)\n'not positive'\n"
          ">>> first_error([pos, even_v], 3)\n'not even'\n"
          ">>> first_error([], 0) is None\nTrue",
 "solution": "first_error = lambda validators, x: find(lambda e: e is not None,\n"
             "                                          map_(lambda v: v(x), validators))",
 "note": "map_ runs every validator, find returns the first non-None (the first failure), else None. "
         "The None-is-Nothing convention makes 'no error' and 'passed' the same value.",
},
{
 "id": "16.12", "level": "challenge", "title": "Curried lookup chain",
 "statement": "Build get_in(keys) -- a function that, given nested dicts, walks the key path and "
              "returns\n"
              "the leaf, or None if any key is missing. get_in is CURRIED: get_in(['a', 'b']) returns "
              "a\n"
              "function you can reuse on many dicts. Fold the keys with a safe step that stops at None.",
 "contract": "get_in(keys: list) -> (dict -> value | None)",
 "tests": ">>> deep = {'a': {'b': {'c': 42}}}\n"
          ">>> get_in(['a', 'b', 'c'])(deep)\n42\n"
          ">>> get_in(['a', 'x'])(deep) is None\nTrue\n"
          ">>> get_in([])(deep) == deep\nTrue\n"
          ">>> pluck = get_in(['a', 'b'])\n>>> pluck(deep)\n{'c': 42}",
 "solution": "def get_in(keys):\n"
             "    def step(d, k):\n"
             "        return d[k] if isinstance(d, dict) and k in d else None\n"
             "    return lambda d: foldl(step, keys, d)",
 "note": "get_in returns a closure over keys -- currying by hand -- so a path becomes a reusable "
         "accessor. The fold threads the dict through each key, poisoning to None on any miss.",
},
]
