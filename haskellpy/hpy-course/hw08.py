TITLE = 'Monoids at Work'

ITEMS = [
    {
        'id': '8.1',
        'level': 'drill',
        'title': 'Min and max, one pass',
        'statement': 'Both extremes of a numeric stream in a single traversal, point-free.',
        'contract': 'extremes(xs) -> (min, max)',
        'tests': '>>> extremes([3, 1, 4, 1, 5])\n(1, 5)',
        'solution': 'extremes = partial(foldMap, lambda x: (x, x), both(MinM, MaxM))',
        'note': 'both fuses two folds into one pass -- what matters when xs is a one-shot iterator or a large file.',
    },
    {
        'id': '8.2',
        'level': 'applied',
        'title': 'Stream statistics',
        'statement': 'Count, total and maximum of a stream in ONE pass: ((count, total), maximum).',
        'contract': 'stats(xs) -> ((n, total), mx)',
        'tests': '>>> stats([3, 1, 4])\n((3, 8), 4)',
        'solution': 'stats = partial(foldMap, lambda x: ((1, x), x), both(both(Sum, Sum), MaxM))',
        'note': 'both nests: a monoid of monoids. The tuple shape of the answer mirrors the shape of the fold.',
    },
    {
        'id': '8.3',
        'level': 'drill',
        'title': 'Config layering',
        'statement': 'defaults, file, cli -- highest layer that DEFINES a key wins, and defining it as None counts. Point-free over the layer list.',
        'contract': 'effective(layers, k) -> Maybe value',
        'tests': ">>> layers = [{'v': 1}, {}, {'v': None}]\n>>> effective(layers, 'v') is None\nTrue\n>>> effective(layers, 'x') is NOTHING\nTrue",
        'solution': 'effective = lambda layers, k: mconcat(Last, [maybe_get(d, k) for d in layers])',
        'note': 'Last with a NOTHING identity is override semantics verbatim. Same skeleton as 4.5 with the opposite monoid.',
    },
    {
        'id': '8.4',
        'level': 'drill',
        'title': 'Flatten',
        'statement': 'Concatenate a list of lists by monoid fold.',
        'contract': 'flatten(xss) -> [x]',
        'tests': '>>> flatten([[1], [], [2, 3]])\n[1, 2, 3]',
        'solution': 'flatten = partial(mconcat, ListM)',
        'note': "Recognize-it: concatenation is the list monoid's mconcat. (For huge inputs reach for itertools.chain -- this one is quadratic.)",
    },
]
