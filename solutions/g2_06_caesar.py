"""06_caesar -- Caesar cipher, letters only, case preserved.

Contract:
    caesar(s: str, k: int) -> str

Hint:
    map_ a per-char shift over the string; the wrap is mod 26 on
    ord() offsets; join the pieces. One helper, one map.

>>> caesar("abc", 2)
'cde'
>>> caesar("XYZ", 3)
'ABC'
>>> caesar("a-b", 1)
'b-c'
>>> caesar("Hello, World!", 13)
'Uryyb, Jbeyq!'
>>> caesar("abc", 0)
'abc'
"""

# -- prelude --
map_      = lambda f, xs: [f(x) for x in xs]

# solution goes here
def caesar(s, k):
    def shift(c):
        if not c.isalpha():
            return c
        base = ord("A") if c.isupper() else ord("a")
        return chr(base + (ord(c) - base + k) % 26)
    return "".join(map_(shift, s))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"06_caesar: {r.attempted - r.failed}/{r.attempted} doctests passing")
