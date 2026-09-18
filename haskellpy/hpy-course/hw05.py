TITLE = 'Either: Failure With a Why'

ITEMS = [
    {
        'id': '5.1',
        'level': 'drill',
        'title': 'Lift the miss into a reason',
        'statement': 'Write get_e(d, k): Ok(value) or Err naming the missing key.',
        'contract': 'get_e(d, k) -> Either',
        'tests': '>>> get_e({\'a\': 1}, \'a\')\n(\'ok\', 1)\n>>> get_e({}, \'user\')\n(\'err\', "missing key: \'user\'")',
        'solution': 'get_e = lambda d, k: note(f"missing key: {k!r}", maybe_get(d, k))',
        'note': 'note is the Maybe-to-Either bridge: same short-circuit, now with a why.',
    },
    {
        'id': '5.2',
        'level': 'applied',
        'title': 'Parse then bound',
        'statement': 'Write to_port(s): parse a decimal string and demand 1..65535, each failure carrying its own message.',
        'contract': 'to_port(s) -> Either',
        'tests': '>>> to_port(\'8080\')\n(\'ok\', 8080)\n>>> to_port(\'http\')\n(\'err\', "not a number: \'http\'")\n>>> to_port(\'99999\')\n(\'err\', \'out of range: 99999\')',
        'solution': 'to_port = lambda s: bindE(\n    note(f"not a number: {s!r}", int(s) if s.isdigit() else NOTHING),\n    lambda n: Ok(n) if 1 <= n <= 65535 else Err(f"out of range: {n}"))',
        'note': 'Two failure modes, two messages, one bindE. The caller pattern-matches once.',
    },
    {
        'id': '5.3',
        'level': 'drill',
        'title': 'First error speaks',
        'statement': 'Validate a batch: all Ok values, or the FIRST Err verbatim.',
        'contract': 'all_ports(ss) -> Either',
        'tests': '>>> all_ports([\'80\', \'443\'])\n(\'ok\', [80, 443])\n>>> all_ports([\'80\', \'x\', \'y\'])\n(\'err\', "not a number: \'x\'")',
        'solution': 'all_ports = lambda ss: sequenceE([to_port(s) for s in ss])',
        'note': 'sequenceE = sequenceM that can explain itself.',
    },
    {
        'id': '5.4',
        'level': 'drill',
        'title': 'Division with a why',
        'statement': 'Write div_e(a, b): the quotient, or an error naming the offense.',
        'contract': 'div_e(a, b) -> Either',
        'tests': ">>> div_e(10, 4)\n('ok', 2.5)\n>>> div_e(1, 0)\n('err', 'division by zero')",
        'solution': "div_e = lambda a, b: Err('division by zero') if b == 0 else Ok(a / b)",
        'note': 'Exceptions escape; Either values travel. Choose Either at module boundaries.',
    },
]
