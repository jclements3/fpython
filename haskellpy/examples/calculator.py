"""calculator.py -- evaluate '2 * (3 + 4) - -5' both ways."""
from haskell import doP, alt, lit, rx, chainl1, runParser, add, sub, mul, partial

# --- imperative ---
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

# --- functional ---
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

# --- demo ---
if __name__ == "__main__":
    cases = ['2 * (3 + 4) - -5', '8 - 3 - 2', '10 / 4', '1 + (2', '1 )']
    for s in cases:
        a, b = calc_imp(s), calc_fn(s)
        assert a[0] == b[0] and (a[0] == 'err' or a[1] == b[1]), (s, a, b)
        print(f"{s!r:22s} imp={a}  fn={b}")
    print("calculator: both agree on all cases")
