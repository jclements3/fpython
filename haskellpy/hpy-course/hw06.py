TITLE = 'do-Notation'

ITEMS = [
    {
        'id': '6.1',
        'level': 'drill',
        'title': 'Config reader, flat',
        'statement': 'Using doM, read host and port from a dict; NOTHING if either is absent.',
        'contract': 'hostport(d) -> Maybe (host, port)',
        'tests': ">>> hostport({'host': 'h', 'port': 80})\n('h', 80)\n>>> hostport({'host': 'h'}) is NOTHING\nTrue",
        'solution': "@doM\ndef hostport(d):\n    h = yield maybe_get(d, 'host')\n    p = yield maybe_get(d, 'port')\n    return (h, p)",
        'note': 'Compare the bind pyramid this replaces: each yield is one >>=, and the failure path is invisible.',
    },
    {
        'id': '6.2',
        'level': 'applied',
        'title': 'Join across two tables',
        'statement': 'users maps id to name; emails maps name to address. Using doM, resolve an id to its address.',
        'contract': 'address(users, emails, uid) -> Maybe str',
        'tests': ">>> u, e = {1: 'ada'}, {'ada': 'ada@x.io'}\n>>> address(u, e, 1)\n'ada@x.io'\n>>> address(u, e, 2) is NOTHING\nTrue",
        'solution': '@doM\ndef address(users, emails, uid):\n    name = yield maybe_get(users, uid)\n    return (yield maybe_get(emails, name))',
        'note': "A two-hop join is two yields. The second bind consumes the first's value by name, not by nesting.",
    },
    {
        'id': '6.3',
        'level': 'applied',
        'title': 'Validated record',
        'statement': 'Using doE, build a user record from a form dict: name must be non-empty, age must parse and land in 0..130. Each rejection explains itself.',
        'contract': 'mk_user(form) -> Either dict',
        'tests': '>>> mk_user({\'name\': \'ada\', \'age\': \'36\'})\n(\'ok\', {\'name\': \'ada\', \'age\': 36})\n>>> mk_user({\'name\': \'\', \'age\': \'36\'})\n(\'err\', \'empty name\')\n>>> mk_user({\'name\': \'ada\', \'age\': \'old\'})\n(\'err\', "bad age: \'old\'")',
        'solution': '@doE\ndef mk_user(form):\n    name = yield (Ok(form.get(\'name\', \'\')) if form.get(\'name\') else Err(\'empty name\'))\n    raw  = form.get(\'age\', \'\')\n    age  = yield note(f"bad age: {raw!r}", int(raw) if raw.isdigit() else NOTHING)\n    yield (Ok(age) if age <= 130 else Err(f\'implausible age: {age}\'))\n    return Ok({\'name\': name, \'age\': age})',
        'note': 'A bare yield with no binding is a guard: run the check, keep no value. The happy path reads top to bottom.',
    },
    {
        'id': '6.4',
        'level': 'drill',
        'title': 'Chained arithmetic',
        'statement': 'Using doE and div_e from 5.4, compute a/b + c/d with the first bad divisor reported.',
        'contract': 'sum_of_ratios(a, b, c, d) -> Either',
        'tests': ">>> sum_of_ratios(1, 2, 1, 4)\n('ok', 0.75)\n>>> sum_of_ratios(1, 0, 1, 4)\n('err', 'division by zero')",
        'solution': '@doE\ndef sum_of_ratios(a, b, c, d):\n    x = yield div_e(a, b)\n    y = yield div_e(c, d)\n    return Ok(x + y)',
        'note': 'Error plumbing gone; only the arithmetic remains.',
    },
]
