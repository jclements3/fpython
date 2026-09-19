TITLE = 'do-Notation'

ITEMS = [
    {
        'id': '7.1',
        'level': 'drill',
        'title': 'Config reader, flat',
        'statement': 'Using doM, read host and port from a dict; NOTHING if either is absent.',
        'contract': 'hostport(d) -> Maybe (host, port)',
        'tests': ">>> hostport({'host': 'h', 'port': 80})\n('h', 80)\n>>> hostport({'host': 'h'}) is NOTHING\nTrue",
        'solution': "@doM\ndef hostport(d):\n    h = yield maybe_get(d, 'host')\n    p = yield maybe_get(d, 'port')\n    return (h, p)",
        'note': "@doM turns an ordinary generator into a Maybe pipeline: each yield hands a Maybe value to doM's machinery, which unwraps it and sends the unwrapped value back into the generator as the result of that yield expression if it's real, or aborts the WHOLE function with NOTHING the instant any yield produces NOTHING. Written this way, hostport reads as two straight-line lookups with no visible branching, even though either one could fail.",
    },
    {
        'id': '7.2',
        'level': 'applied',
        'title': 'Join across two tables',
        'statement': 'users maps id to name; emails maps name to address. Using doM, resolve an id to its address.',
        'contract': 'address(users, emails, uid) -> Maybe str',
        'tests': ">>> u, e = {1: 'ada'}, {'ada': 'ada@x.io'}\n>>> address(u, e, 1)\n'ada@x.io'\n>>> address(u, e, 2) is NOTHING\nTrue",
        'solution': '@doM\ndef address(users, emails, uid):\n    name = yield maybe_get(users, uid)\n    return (yield maybe_get(emails, name))',
        'note': "The same @doM discipline, but the second lookup's key depends on the FIRST lookup's result: name = yield maybe_get(users, uid) must succeed and bind name before maybe_get(emails, name) can even be attempted. If uid isn't in users, the function stops at the first yield and never reaches the second lookup -- there is nothing to explicitly check for that.",
    },
    {
        'id': '7.3',
        'level': 'applied',
        'title': 'Validated record',
        'statement': 'Using doE, build a user record from a form dict: name must be non-empty, age must parse and land in 0..130. Each rejection explains itself.',
        'contract': 'mk_user(form) -> Either dict',
        'tests': '>>> mk_user({\'name\': \'ada\', \'age\': \'36\'})\n(\'ok\', {\'name\': \'ada\', \'age\': 36})\n>>> mk_user({\'name\': \'\', \'age\': \'36\'})\n(\'err\', \'empty name\')\n>>> mk_user({\'name\': \'ada\', \'age\': \'old\'})\n(\'err\', "bad age: \'old\'")',
        'solution': '@doE\ndef mk_user(form):\n    name = yield (Ok(form.get(\'name\', \'\')) if form.get(\'name\') else Err(\'empty name\'))\n    raw  = form.get(\'age\', \'\')\n    age  = yield note(f"bad age: {raw!r}", int(raw) if raw.isdigit() else NOTHING)\n    yield (Ok(age) if age <= 130 else Err(f\'implausible age: {age}\'))\n    return Ok({\'name\': name, \'age\': age})',
        'note': 'This doE pipeline mixes VALUE-producing yields (which bind name and age for later use) with one bare, unbound yield -- the age <= 130 check -- that runs purely for its side effect of stopping the pipeline if it fails; nothing from that check is kept, it exists only to guard what comes after. Read top to bottom, the happy path (every field valid) is the only path visible, and every rejection reason sits as an Err right at the line that would fail it.',
    },
    {
        'id': '7.4',
        'level': 'drill',
        'title': 'Chained arithmetic',
        'statement': 'Using doE and div_e from 6.4, compute a/b + c/d with the first bad divisor reported.',
        'contract': 'sum_of_ratios(a, b, c, d) -> Either',
        'tests': ">>> sum_of_ratios(1, 2, 1, 4)\n('ok', 0.75)\n>>> sum_of_ratios(1, 0, 1, 4)\n('err', 'division by zero')",
        'solution': '@doE\ndef sum_of_ratios(a, b, c, d):\n    x = yield div_e(a, b)\n    y = yield div_e(c, d)\n    return Ok(x + y)',
        'note': "Two divisions, each already Either-safe via div_e, are bound in sequence with doE: x captures the first ratio, y the second, and if EITHER division is by zero, the whole function short-circuits to that division's Err without ever reaching the addition. The final line is pure arithmetic with no visible error-handling code, because doE has already absorbed all of it.",
    },
]
