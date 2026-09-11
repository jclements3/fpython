"""02_eval_rpn -- Evaluate Reverse Polish notation.

Integer operands, operators + - *.

Contract:
    eval_rpn(tokens: list[str]) -> int

Hint:
    One fold over the tokens: operands push; an operator pops two and
    pushes the result. The classic slip: stack[-2] is the LEFT
    operand. The answer is whatever the fold leaves on the stack.

>>> eval_rpn(["2", "3", "+", "4", "*"])
20
>>> eval_rpn(["5", "1", "2", "+", "4", "*", "-"])
-7
>>> eval_rpn(["7"])
7
"""

# -- prelude --
NOTHING   = object()              # Maybe's Nothing: "no arg given"; test with `is` (pattern match)

def foldl(f, xs, init=NOTHING):           # THE left fold; Python buried its own in functools as reduce
    it = iter(xs)
    if init is NOTHING:
        try:
            acc = next(it)
        except StopIteration:
            raise TypeError("fold of empty sequence with no initial value")
    else:
        acc = init
    for x in it:
        acc = f(acc, x)
    return acc

# solution goes here
OPS = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
       "*": lambda a, b: a * b}

def eval_rpn(tokens):
    def step(stack, tok):
        if tok in OPS:
            return stack[:-2] + [OPS[tok](stack[-2], stack[-1])]
        return stack + [int(tok)]
    return foldl(step, tokens, [])[0]


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"02_eval_rpn: {r.attempted - r.failed}/{r.attempted} doctests passing")
