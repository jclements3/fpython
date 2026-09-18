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

# --- oop ---
class GradeBook:
    """The same job, encapsulated: a mutable object that grows by .add(row),
    raising on the first bad row instead of returning an Err tuple."""
    def __init__(self):
        self.rows = []

    def add(self, row):
        name, _, raw = row.partition(',')
        if not name:
            raise ValueError(f'empty name in {row!r}')
        if not raw.strip().isdigit():
            raise ValueError(f'bad score in {row!r}')
        score = int(raw)
        if score > 100:
            raise ValueError(f'score > 100 in {row!r}')
        self.rows.append((name, score))
        return self                                   # chainable: book.add(r1).add(r2)

    def stats(self):
        n = len(self.rows)
        tot = sum(s for _, s in self.rows)
        best = max((s for _, s in self.rows), default=float('-inf'))
        return (n, tot), best

def admit_oop(rows):
    book = GradeBook()
    try:
        for row in rows:
            book.add(row)
    except ValueError as e:
        return ('err', str(e))
    return ('ok', (book.rows, *book.stats()))

# --- demo ---
if __name__ == "__main__":
    for rows in (ROWS, BAD):
        a, b, c = admit_imp(rows), admit_fn(rows), admit_oop(rows)
        assert a == b == c, (rows, a, b, c)
        print(("ok  :" if a[0] == "ok" else "err :"), b)
    print("gradebook: all three agree")
