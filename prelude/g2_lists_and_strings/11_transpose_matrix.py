"""11_transpose_matrix -- Flip rows and columns.

Contract:
    transpose_matrix(rows: list[list]) -> list[list]

Hint:
    This IS the prelude's transpose -- like flatten was concat.
    One name, zero work; know WHY zip(*rows) does it.

>>> transpose_matrix([[1, 2, 3], [4, 5, 6]])
[[1, 4], [2, 5], [3, 6]]
>>> transpose_matrix([[5]])
[[5]]
>>> transpose_matrix([[7], [8], [9]])
[[7, 8, 9]]
"""

# -- prelude --
def transpose(xss):                         # Data.List: rows <-> cols, RAGGED-SAFE like Haskell --
    xss = [list(xs) for xs in xss]          # short rows just drop out of later columns (no truncation)
    n = max(map(len, xss), default=0)
    return [[xs[i] for xs in xss if i < len(xs)] for i in range(n)]

# solution goes here


if __name__ == u'__main__':
    import doctest
    r = doctest.testmod()
    print(f"11_transpose_matrix: {r.attempted - r.failed}/{r.attempted} doctests passing")
