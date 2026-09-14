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
def takewhile(crit, xs):
    for x in xs:
        if not crit(x):
            return
        yield x

def dropwhile(crit, xs):
    it = iter(xs)
    for x in it:
        if not crit(x):
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


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"05_calculator: {r.attempted - r.failed}/{r.attempted} doctests passing")
