"""03_fizzbuzz -- FizzBuzz as data.

For 1..n: multiples of 3 -> "Fizz", of 5 -> "Buzz", of both ->
"FizzBuzz", else the number as a string.

Contract:
    fizzbuzz(n: int) -> list[str]

Hint:
    Solve it BOTH ways and compare -- the contrast is the lesson:
    1. COMPOSITION OF ARMS: map_ one per-number rule over
       range(1, n+1), building the word by concatenating guards --
       "Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) -- with
       `or str(i)` catching the empty case. Overlaps compose:
       15 earns "FizzBuzz" from two rules for free.
    2. FIRST-MATCH SELECTION: a RULES table of (predicate, result)
       pairs, find picking the first hit; const(otherwise) is the
       catch-all arm. Overlaps need their own row (15 goes first),
       but the ladder is now DATA -- appendable, testable rule by
       rule. Which generalizes better depends on whether cases
       overlap.

>>> fizzbuzz(5)
['1', '2', 'Fizz', '4', 'Buzz']
>>> fizzbuzz(15)[-1]
'FizzBuzz'
>>> fizzbuzz(0)
[]
"""

# -- prelude --
const     = lambda x: lambda _: x

otherwise = True

fst  = lambda p: p[0]

snd  = lambda p: p[1]

map_      = lambda f, xs: [f(x) for x in xs]

# Data.List find: lazy first-match -- folds can't stop early, find can
find      = lambda pred, xs: next((x for x in xs if pred(x)), None)   # first match, else None

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"03_fizzbuzz: {r.attempted - r.failed}/{r.attempted} doctests passing")
