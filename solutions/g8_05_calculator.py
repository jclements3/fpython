"""05_calculator -- Integer expression evaluator (capstone).

+, -, * and parentheses, optional spaces, normal precedence,
left-associative. No unary minus, no division.

Contract:
    evaluate(expr: str) -> int

Grammar (one function per rule, shared position cursor):
    expression := term (('+' | '-') term)*
    term       := factor ('*' factor)*
    factor     := NUMBER | '(' expression ')'

Hint:
    Recursive descent. Lex numbers with takeWhile str.isdigit on the
    remaining input -- span IS the lexer. And remember the trap you
    certified earlier: '' in "+-" is True; test membership against a
    tuple.

>>> evaluate("2*(3+4)")
14
>>> evaluate("2*(3+4)-5")
9
>>> evaluate("10-2-3")
5
>>> evaluate("2+3*4")
14
>>> evaluate("((1+2))*3")
9
>>> evaluate(" 12 * 2 ")
24
"""

# -- prelude --
def takewhile(cond, xs):
    for x in xs:
        if not cond(x):
            return
        yield x

def dropwhile(cond, xs):
    it = iter(xs)
    for x in it:
        if not cond(x):
            yield x
            break
    yield from it

takeWhile = lambda p, xs: list(takewhile(p, xs))

dropWhile = lambda p, xs: list(dropwhile(p, xs))

def span(p, xs):                            # split at first failure, ONE pass; safe on one-shot iters
    xs = list(xs)
    i = next((i for i, x in enumerate(xs) if not p(x)), len(xs))
    return (xs[:i], xs[i:])

# solution goes here
def evaluate(expr):
    s = expr.replace(" ", "")
    pos = [0]

    def peek():
        return s[pos[0]] if pos[0] < len(s) else ""

    def number():
        digits = takeWhile(str.isdigit, s[pos[0]:])
        pos[0] += len(digits)
        return int("".join(digits))

    def factor():
        if peek() == "(":
            pos[0] += 1
            v = expression()
            pos[0] += 1
            return v
        return number()

    def term():
        v = factor()
        while peek() == "*":
            pos[0] += 1
            v *= factor()
        return v

    def expression():
        v = term()
        while peek() in ("+", "-"):
            op = peek()
            pos[0] += 1
            v = v + term() if op == "+" else v - term()
        return v

    return expression()


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_calculator: {r.attempted - r.failed}/{r.attempted} doctests passing")
