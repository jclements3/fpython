TITLE = 'Capstone Labs'

ITEMS = [
    {
        'id': '9.1',
        'level': 'lab',
        'title': 'The algebraic calculator',
        'statement': 'Full expression evaluator: + - * /, precedence, LEFT associativity, unary minus, parentheses, decimals, whitespace; Either out.',
        'contract': 'calc(s) -> Either float',
        'tests': ">>> calc('2 * (3 + 4) - -5')\n('ok', 19.0)\n>>> calc('8 - 3 - 2')\n('ok', 3.0)\n>>> calc('2 * (3 +')[0]\n'err'",
        'solution': "number = rx(r'-?\\d+(\\.\\d+)?', float)\n@doP\ndef _paren():\n    yield lit('(')\n    v = yield expr\n    yield lit(')')\n    return v\nunary = lambda s: alt(number, _paren())(s)\nterm  = chainl1(unary, {'*': mul, '/': lambda a, b: a / b})\nexpr  = chainl1(term,  {'+': add, '-': sub})\ncalc  = partial(runParser, expr)",
        'note': 'Eight grammar lines. Every layer earns its keep: doP threads state, chainl1 folds associativity, runParser explains failure. 5000-term chains run in constant stack.',
    },
    {
        'id': '9.2',
        'level': 'lab',
        'title': 'INI reader',
        'statement': 'Parse [section] headers with key = value bodies into a dict of dicts.',
        'contract': 'ini(s) -> Either {section: {k: v}}',
        'tests': ">>> t = '[db]\\nhost = local\\nport = 5432\\n[app]\\ndebug = true'\n>>> ini(t)\n('ok', {'db': {'host': 'local', 'port': '5432'}, 'app': {'debug': 'true'}})",
        'solution': "@doP\ndef _kvi():\n    k = yield rx(r'\\w+')\n    yield lit('=')\n    v = yield rx(r'[^\\n\\[]+', str.strip)\n    return (k, v)\n@doP\ndef _section():\n    yield lit('[')\n    name = yield rx(r'\\w+')\n    yield lit(']')\n    kvs = yield many(_kvi())\n    return (name, dict(kvs))\nini = lambda s: bindE(runParser(many(_section()), s), o(Ok, dict))",
        'note': 'The 7.2 skeleton, nested once. many loops, so thousand-key files cost no stack; bindE lifts the final dict without unwrapping by hand.',
    },
    {
        'id': '9.3',
        'level': 'lab',
        'title': 'Log triage',
        'statement': "Lines are 'LEVEL message'. In ONE pass report ((errors, total), first ERROR message or NOTHING).",
        'contract': 'triage(lines) -> ((errors, total), first_err)',
        'tests': ">>> triage(['INFO up', 'ERROR db down', 'ERROR retry', 'INFO ok'])\n((2, 4), 'db down')\n>>> triage(['INFO up'])[1] is NOTHING\nTrue",
        'solution': "tag = lambda ln: (lambda lvl, _, msg: ((lvl == 'ERROR', 1),\n                  msg if lvl == 'ERROR' else NOTHING))(*ln.partition(' '))\ntriage = partial(foldMap, tag, both(both(Sum, Sum), First))",
        'note': 'Counting and first-witness are DIFFERENT monoids riding the same pass. Adding a new statistic is one more both, not another loop.',
    },
    {
        'id': '9.4',
        'level': 'lab',
        'title': 'Batch admission',
        'statement': "Admit a batch of form dicts with 6.3's mk_user: all records, or the first rejection verbatim.",
        'contract': 'admit(forms) -> Either [dict]',
        'tests': ">>> admit([{'name': 'ada', 'age': '36'}, {'name': 'bob', 'age': '41'}])\n('ok', [{'name': 'ada', 'age': 36}, {'name': 'bob', 'age': 41}])\n>>> admit([{'name': 'ada', 'age': '36'}, {'name': '', 'age': '2'}])\n('err', 'empty name')",
        'solution': 'admit = o(sequenceE, partial(map, mk_user), list)',
        'note': 'Validation composes: per-record doE, batch-level sequenceE, glued point-free. The whole intake pipeline is one line.',
    },
]
