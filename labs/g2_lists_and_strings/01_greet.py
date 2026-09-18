"""01_greet -- Greeting string.

Contract:
    greet(name: str) -> 'Hello, <name>!'

Hint:
    unwords joins words with single spaces; the bang concatenates.
    Trivial on purpose -- the warmup proves the pipeline.

>>> greet("Ada")
'Hello, Ada!'
>>> greet("world")
'Hello, world!'
"""

# -- prelude --
unwords = " ".join

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"01_greet: {r.attempted - r.failed}/{r.attempted} doctests passing")
