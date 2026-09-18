# Imperative vs Functional -- ten small apps on `haskell.py`

Each app below ships as a runnable file in `examples/`: an imperative
implementation and a functional one over the same inputs, with a `__main__`
block that ASSERTS the two agree. Every code block in this document is
extracted verbatim from those files (and verified to run and agree before
this document is generated), so what you read is what was executed.

Run any of them: `PYTHONPATH=.. python3 examples/<name>.py`.

## calculator.py -- evaluate '2 * (3 + 4) - -5' both ways

### Imperative

```python
def calc_imp(s):
    toks, i = [], 0                                   # 1. tokenize with an index
    while i < len(s):
        c = s[i]
        if c.isspace(): i += 1; continue
        if c in '+-*/()': toks.append(c); i += 1; continue
        if c.isdigit():
            j = i
            while j < len(s) and (s[j].isdigit() or s[j] == '.'): j += 1
            toks.append(float(s[i:j])); i = j; continue
        return ('err', f'bad char {c!r}')

    class P:                                          # 2. parse with a mutable cursor
        pos = 0
    def peek(): return toks[P.pos] if P.pos < len(toks) else None
    def unary():
        t = peek()
        if t == '-': P.pos += 1; return -unary()
        if t == '(':
            P.pos += 1; v = expr()
            if peek() != ')': raise ValueError('expected )')
            P.pos += 1; return v
        if isinstance(t, float): P.pos += 1; return t
        raise ValueError(f'unexpected {t!r}')
    def term():
        v = unary()
        while peek() in ('*', '/'):
            op = peek(); P.pos += 1; w = unary()
            v = v * w if op == '*' else v / w
        return v
    def expr():
        v = term()
        while peek() in ('+', '-'):
            op = peek(); P.pos += 1; w = term()
            v = v + w if op == '+' else v - w
        return v

    try:                                              # 3. errors ride exceptions
        v = expr()
        return ('ok', v) if P.pos == len(toks) else ('err', 'unconsumed input')
    except ValueError as e:
        return ('err', str(e))
```

### Functional

```python
number = rx(r'-?\d+(\.\d+)?', float)
@doP
def _paren():
    yield lit('(')
    v = yield expr_fn
    yield lit(')')
    return v
unary_fn = lambda s: alt(number, _paren())(s)
term_fn  = chainl1(unary_fn, {'*': mul, '/': lambda a, b: a / b})
expr_fn  = chainl1(term_fn,  {'+': add, '-': sub})
calc_fn  = partial(runParser, expr_fn)
```

## gradebook.py -- validate 'name,score' rows, then one-pass class stats

### Imperative

```python
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
```

### Functional

```python
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
```

## layers.py -- layered config: defaults < file < cli; None is a real value

### Imperative

```python
_UNSET = object()                                     # invent a private sentinel,
def effective_imp(layers, k):                         # because None must survive
    val = _UNSET
    for d in layers:
        if k in d:
            val = d[k]
    return NOTHING if val is _UNSET else val

def merged_imp(layers):
    out = {}
    for d in layers:
        for k, v in d.items():
            out[k] = v
    return out
```

### Functional

```python
effective_fn = lambda layers, k: mconcat(Last, [maybe_get(d, k) for d in layers])
merged_fn    = lambda layers: foldl(lambda a, b: unionWith(lambda old, new: new, a, b),
                                    layers, {})
```

## leaderboard.py -- clamp scores into [0, 100], rank by score desc, name asc

### Imperative

```python
def rank_imp(rows):
    clamped = []
    for name, score in rows:
        if score < 0:
            score = 0
        elif score > 100:
            score = 100
        clamped.append((name, score))
    clamped.sort(key=lambda r: (-r[1], r[0]))          # score desc, name asc
    return clamped
```

### Functional

```python
clamp = lambda lo, hi: o(partial(max, lo), partial(min, hi))
clamp100 = clamp(0, 100)
name_of, score_of = itemgetter(0), itemgetter(1)
rank_fn = lambda rows: sortOn(
    lambda r: (-score_of(r), name_of(r)),
    [(name_of(r), clamp100(score_of(r))) for r in rows])
```

## logtriage.py -- 'LEVEL message' lines: error count, total, first error message

### Imperative

```python
def triage_imp(lines):
    errors = 0                                        # three mutable slots
    total = 0
    first = None                                      # and a hand-rolled sentinel:
    seen_first = False                                # None alone can't mean "none yet"
    for ln in lines:                                  # if a message could be empty
        lvl, _, msg = ln.partition(' ')
        total += 1
        if lvl == 'ERROR':
            errors += 1
            if not seen_first:
                first, seen_first = msg, True
    return ((errors, total), first if seen_first else NOTHING)
```

### Functional

```python
tag = lambda ln: (lambda lvl, _, msg:
                  ((lvl == 'ERROR', 1), msg if lvl == 'ERROR' else NOTHING)
                  )(*ln.partition(' '))
triage_fn = partial(foldMap, tag, both(both(Sum, Sum), First))
```

## orderbatch.py -- capstone: validate a batch of orders (qty > 0, price > 0), computing each line total; the whole batch fails at the first bad order, carrying which one and why

### Imperative

```python
def total_imp(order):
    if order["qty"] <= 0:
        return ("err", f"{order['item']}: bad qty {order['qty']}")
    if order["price"] <= 0:
        return ("err", f"{order['item']}: bad price {order['price']}")
    return ("ok", round(order["qty"] * order["price"], 2))

def admit_imp(orders):
    out = []
    for o in orders:
        r = total_imp(o)
        if r[0] == "err":
            return r
        out.append(r[1])
    return ("ok", out)
```

### Functional

```python
@doE
def total_fn(order):
    qty = yield (Ok(order["qty"]) if order["qty"] > 0
                 else Err(f"{order['item']}: bad qty {order['qty']}"))
    price = yield (Ok(order["price"]) if order["price"] > 0
                   else Err(f"{order['item']}: bad price {order['price']}"))
    return Ok(round(qty * price, 2))

admit_fn = lambda orders: sequenceE([total_fn(o) for o in orders])
```

## orgchart.py -- resolve an employee's manager's manager's email, or NOTHING if any hop is missing. None-as-Nothing means a missing hop and a real missing-email must stay distinguishable

### Imperative

```python
def skip_manager_email_imp(emp):
    mgr = MANAGER_OF.get(emp, NOTHING)
    if mgr is NOTHING:
        return NOTHING
    skip = MANAGER_OF.get(mgr, NOTHING)
    if skip is NOTHING:
        return NOTHING
    if skip not in EMAIL_OF:
        return NOTHING
    return EMAIL_OF[skip]
```

### Functional

```python
@doM
def skip_manager_email_fn(emp):
    mgr = yield maybe_get(MANAGER_OF, emp)
    skip = yield maybe_get(MANAGER_OF, mgr)
    return (yield maybe_get(EMAIL_OF, skip))
```

## payoff.py -- loan payoff schedule: balances after each fixed payment, and how many payments until paid off

### Imperative

```python
def schedule_imp(balance, payment, rate):
    out, n = [balance], 0
    while balance > 0:
        balance = round(balance * (1 + rate) - payment, 2)
        if balance < 0:
            balance = 0.0
        out.append(balance)
        n += 1
    return out, n
```

### Functional

```python
def _step(payment, rate):
    def step(balance):
        if balance <= 0:
            return NOTHING
        nxt = round(balance * (1 + rate) - payment, 2)
        nxt = max(nxt, 0.0)
        return (nxt, nxt)
    return step

def schedule_fn(balance, payment, rate):
    rest = unfoldr(_step(payment, rate), balance)
    return [balance] + rest, len(rest)
```

## sensoralert.py -- smooth a sensor stream with a 3-wide moving average, then report each consecutive run of over-threshold readings as (start, len)

### Imperative

```python
def alerts_imp(xs, n, threshold):
    smoothed = []
    for i in range(len(xs) - n + 1):
        window = xs[i:i + n]
        smoothed.append(sum(window) / n)
    flags = [v > threshold for v in smoothed]
    runs, i = [], 0
    while i < len(flags):
        if flags[i]:
            start = i
            while i < len(flags) and flags[i]:
                i += 1
            runs.append((start, i - start))
        else:
            i += 1
    return runs
```

### Functional

```python
def alerts_fn(xs, n, threshold):
    smoothed = [sum(w) / n for w in windows(n, xs)]
    flagged = [(i, v > threshold) for i, v in enum(smoothed)]
    groups = groupBy(lambda a, b: a[1] == b[1], flagged)
    return [(g[0][0], len(g)) for g in groups if g[0][1]]
```

## wordfreq.py -- top-N word frequencies, ties alphabetical

### Imperative

```python
def top_imp(n, text):
    counts = {}                                       # mutate a dict
    for w in text.lower().split():
        if w in counts:
            counts[w] += 1
        else:
            counts[w] = 1
    items = list(counts.items())                      # then sort, then slice
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items[:n]
```

### Functional

```python
top_fn = lambda n, text: pipe(
    text, str.lower, words,
    lambda ws: fromListWith(add, [(w, 1) for w in ws]),
    dict.items, partial(sortOn, lambda kv: (-kv[1], kv[0])),
    partial(take, n))
```
