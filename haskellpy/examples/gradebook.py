"""gradebook.py -- validate 'name,score' rows, then one-pass class stats."""
from haskell import (doE, Ok, Err, note, traverseE, bindE, NOTHING,
                     foldMap, both, Sum, MaxM, o, partial)

ROWS = ['ada,95', 'bob,71', 'eve,88']
BAD  = ['ada,95', ',71', 'eve,eight']

# --- imperative ---
def admit_imp(rows):
    out = []                                          # accumulate + early return
    for row in rows:
        name, _, raw = row.partition(',')
        if not name:
            return ('err', f'empty name in {row!r}')
        if not raw.strip().isdigit():
            return ('err', f'bad score in {row!r}')
        score = int(raw)
        if score > 100:
            return ('err', f'score > 100 in {row!r}')
        out.append((name, score))
    n = tot = 0                                       # second loop for stats
    best = float('-inf')
    for _, s in out:
        n += 1; tot += s
        if s > best: best = s
    return ('ok', (out, (n, tot), best))

# --- functional ---
@doE
def _row(row):
    name, _, raw = row.partition(',')
    yield (Ok(name) if name else Err(f'empty name in {row!r}'))
    s = yield note(f'bad score in {row!r}', int(raw) if raw.strip().isdigit() else NOTHING)
    yield (Ok(s) if s <= 100 else Err(f'score > 100 in {row!r}'))
    return Ok((name, s))

stats    = partial(foldMap, lambda p: ((1, p[1]), p[1]), both(both(Sum, Sum), MaxM))
admit_fn = lambda rows: bindE(traverseE(_row, rows),
                              lambda ps: Ok((ps, *stats(ps))))

# --- demo ---
if __name__ == "__main__":
    a, b = admit_imp(ROWS), admit_fn(ROWS)
    assert a == b, (a, b)
    print("ok  :", b)
    a, b = admit_imp(BAD), admit_fn(BAD)
    assert a == b, (a, b)
    print("err :", b)
    print("gradebook: both agree")
