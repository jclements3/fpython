TITLE = 'Monoids at Work'

ITEMS = [
    {
        'id': '9.1',
        'level': 'drill',
        'title': 'Min and max, one pass',
        'statement': 'Both extremes of a numeric stream in a single traversal, point-free.',
        'contract': 'extremes(xs) -> (min, max)',
        'tests': '>>> extremes([3, 1, 4, 1, 5])\n(1, 5)',
        'solution': 'extremes = partial(foldMap, lambda x: (x, x), both(MinM, MaxM))',
        'note': "foldMap first turns each element x into the pair (x, x) -- one copy destined for the min side, one for the max side -- and both(MinM, MaxM) runs MinM's fold on the first half of every pair and MaxM's fold on the second half, all in a SINGLE traversal of xs. That matters specifically when xs is a generator or a large file read once: two separate min(xs)/max(xs) calls would each need their own full pass, impossible for a one-shot iterator, but this needs only one.",
    },
    {
        'id': '9.2',
        'level': 'applied',
        'title': 'Stream statistics',
        'statement': 'Count, total and maximum of a stream in ONE pass: ((count, total), maximum).',
        'contract': 'stats(xs) -> ((n, total), mx)',
        'tests': '>>> stats([3, 1, 4])\n((3, 8), 4)',
        'solution': 'stats = partial(foldMap, lambda x: ((1, x), x), both(both(Sum, Sum), MaxM))',
        'note': 'The same one-pass trick as 8.1, nested one level deeper: each element becomes ((1, x), x), and both(both(Sum, Sum), MaxM) applies Sum to the running count, Sum to the running total, and MaxM to the running maximum, all three statistics falling out of three nested monoids fused into a single fold. The output shape, ((n, total), mx), directly mirrors how the monoids were nested inside each other.',
    },
    {
        'id': '9.3',
        'level': 'drill',
        'title': 'Config layering',
        'statement': 'defaults, file, cli -- highest layer that DEFINES a key wins, and defining it as None counts. Point-free over the layer list.',
        'contract': 'effective(layers, k) -> Maybe value',
        'tests': ">>> layers = [{'v': 1}, {}, {'v': None}]\n>>> effective(layers, 'v') is None\nTrue\n>>> effective(layers, 'x') is NOTHING\nTrue",
        'solution': 'effective = lambda layers, k: mconcat(Last, [maybe_get(d, k) for d in layers])',
        'note': "mconcat folds the list of per-layer lookups through the Last monoid, whose rule -- ``the most recent non-NOTHING value wins'' -- is precisely ``later layers override earlier ones''. Because Last's identity is NOTHING, a key present in no layer at all correctly yields NOTHING with no base case to write. This is the exact same skeleton as first_set in 5.5, with only the monoid swapped (Last instead of First) to flip which end of the list wins.",
    },
    {
        'id': '9.4',
        'level': 'drill',
        'title': 'Flatten',
        'statement': 'Concatenate a list of lists by monoid fold.',
        'contract': 'flatten(xss) -> [x]',
        'tests': '>>> flatten([[1], [], [2, 3]])\n[1, 2, 3]',
        'solution': 'flatten = partial(mconcat, ListM)',
        'note': "mconcat(ListM, xss) folds the list of lists through ListM, the monoid whose identity is [] and whose op is list concatenation -- which is precisely what ``flatten a list of lists'' means. partial freezes ListM in, so flatten ends up a plain one-argument function. The quadratic-cost warning matters because repeated concatenation re-copies earlier elements on every combine; fine for a handful of sublists, but itertools.chain is the right tool once there are many large ones.",
    },
]
