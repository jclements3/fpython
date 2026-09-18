"""08_rle_encode -- Run-length encode.

"aaabbc" -> "a3b2c1"; every run gets a count, even runs of one.

Contract:
    rle_encode(s: str) -> str

Hint:
    The prelude's group gathers runs of CONSECUTIVE equals as bare
    lists. map_ each run to run[0] + str(len(run)), join.

>>> rle_encode("aaabbc")
'a3b2c1'
>>> rle_encode("abc")
'a1b1c1'
>>> rle_encode("aaaa")
'a4'
>>> rle_encode("")
''
"""

# -- prelude --
def groupBy(eq, xs):                        # Data.List groupBy: runs of CONSECUTIVE elements; each new
    out = []                                # element is compared via eq against the run's FIRST element,
    for x in xs:                            # exactly like Haskell (span-based) -- not its neighbor
        if out and eq(out[-1][0], x):
            out[-1].append(x)
        else:
            out.append([x])
    return out

group = lambda xs: groupBy(lambda a, b: a == b, xs)   # Data.List group: runs of equals, [[a]] -- no keys

map_      = lambda f, xs: [f(x) for x in xs]

# solution goes here
rle_encode = lambda s: "".join(
    map_(lambda run: run[0] + str(len(run)), group(s)))


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"08_rle_encode: {r.attempted - r.failed}/{r.attempted} doctests passing")
