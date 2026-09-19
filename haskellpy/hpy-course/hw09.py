TITLE = 'Capstone Labs'

ITEMS = [
    {
        'id': '10.1',
        'level': 'lab',
        'title': 'The algebraic calculator',
        'statement': 'Full expression evaluator: + - * /, precedence, LEFT associativity, unary minus, parentheses, decimals, whitespace; Either out.',
        'contract': 'calc(s) -> Either float',
        'tests': ">>> calc('2 * (3 + 4) - -5')\n('ok', 19.0)\n>>> calc('8 - 3 - 2')\n('ok', 3.0)\n>>> calc('2 * (3 +')[0]\n'err'",
        'solution': "number = rx(r'-?\\d+(\\.\\d+)?', float)\n@doP\ndef _paren():\n    yield lit('(')\n    v = yield expr\n    yield lit(')')\n    return v\nunary = lambda s: alt(number, _paren())(s)\nterm  = chainl1(unary, {'*': mul, '/': lambda a, b: a / b})\nexpr  = chainl1(term,  {'+': add, '-': sub})\ncalc  = partial(runParser, expr)",
        'note': 'A small recursive-descent grammar in three layers: unary handles a bare number OR a fully parenthesized sub-expression (recursing back into expr for whatever is inside the parens), term folds a sequence of unary results left to right through * and /, and expr folds a sequence of term results left to right through + and - -- together enforcing standard precedence purely through which layer calls which. doP threads the remaining input through every yield with no explicit position variable, chainl1 does the left-associative folding, and runParser turns the result into an Either that names exactly where parsing failed. Because none of this recurses per TOKEN (only per parenthesis nesting level), a long flat expression with thousands of terms still runs in constant stack depth.',
    },
    {
        'id': '10.2',
        'level': 'lab',
        'title': 'INI reader',
        'statement': 'Parse [section] headers with key = value bodies into a dict of dicts.',
        'contract': 'ini(s) -> Either {section: {k: v}}',
        'tests': ">>> t = '[db]\\nhost = local\\nport = 5432\\n[app]\\ndebug = true'\n>>> ini(t)\n('ok', {'db': {'host': 'local', 'port': '5432'}, 'app': {'debug': 'true'}})",
        'solution': "@doP\ndef _kvi():\n    k = yield rx(r'\\w+')\n    yield lit('=')\n    v = yield rx(r'[^\\n\\[]+', str.strip)\n    return (k, v)\n@doP\ndef _section():\n    yield lit('[')\n    name = yield rx(r'\\w+')\n    yield lit(']')\n    kvs = yield many(_kvi())\n    return (name, dict(kvs))\nini = lambda s: bindE(runParser(many(_section()), s), o(Ok, dict))",
        'note': '_kvi parses one key=value line, reusing the exact shape built in 8.2, and _section parses a bracketed header followed by ZERO OR MORE key/value lines via many(_kvi()); many loops rather than recurses, so an arbitrarily long -- or empty -- section body costs no extra stack. The top-level ini parser is many(_section()) run through runParser, and o(Ok, dict) takes the raw list of (name, {k: v}) pairs on success and wraps it as {name: {k: v}} inside an Ok, all in one composed step.',
    },
    {
        'id': '10.3',
        'level': 'lab',
        'title': 'Log triage',
        'statement': "Lines are 'LEVEL message'. In ONE pass report ((errors, total), first ERROR message or NOTHING).",
        'contract': 'triage(lines) -> ((errors, total), first_err)',
        'tests': ">>> triage(['INFO up', 'ERROR db down', 'ERROR retry', 'INFO ok'])\n((2, 4), 'db down')\n>>> triage(['INFO up'])[1] is NOTHING\nTrue",
        'solution': "tag = lambda ln: (lambda lvl, _, msg: ((lvl == 'ERROR', 1),\n                  msg if lvl == 'ERROR' else NOTHING))(*ln.partition(' '))\ntriage = partial(foldMap, tag, both(both(Sum, Sum), First))",
        'note': "tag turns each log line into a nested tuple shaped exactly like the monoid that will consume it: ((is_it_an_error, 1), the_error_message_or_NOTHING). both(both(Sum, Sum), First) then counts errors, counts total lines, and remembers the first error's message, all as three independent monoids riding the SAME single pass over the lines. Adding a fourth statistic later means nesting one more both and extending tag's output tuple by one field, not adding a second loop.",
    },
    {
        'id': '10.4',
        'level': 'lab',
        'title': 'Batch admission',
        'statement': "Admit a batch of form dicts with 7.3's mk_user: all records, or the first rejection verbatim.",
        'contract': 'admit(forms) -> Either [dict]',
        'tests': ">>> admit([{'name': 'ada', 'age': '36'}, {'name': 'bob', 'age': '41'}])\n('ok', [{'name': 'ada', 'age': 36}, {'name': 'bob', 'age': 41}])\n>>> admit([{'name': 'ada', 'age': '36'}, {'name': '', 'age': '2'}])\n('err', 'empty name')",
        'solution': 'admit = o(sequenceE, partial(map, mk_user), list)',
        'note': "sequenceE, partial(map, mk_user), and list are composed right to left with o: first every form in the batch runs through mk_user's per-record validation from 7.3, producing a list of Ok/Err results; sequenceE then collapses that list into a single Either -- Ok of every validated record if all passed, or the first Err encountered if any one failed. The whole batch-intake pipeline fits on one line because each piece (mk_user, sequenceE) was already built and verified independently in earlier chapters.",
    },
]
