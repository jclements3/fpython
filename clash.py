r"""clash.py -- the Clash layer over prelude.py, the way clash-prelude layers
over Haskell's Prelude. Import qualified: `import clash as C`.

The whole vocabulary of synchronous hardware, in seven names, on one
convention:

    A Signal IS a section-8 lazy stream: one value per clock tick, forever.

Everything here consumes and yields GENERATORS -- never lists. That is the
Clash discipline: signals are infinite, so only lazy views (C.sampleN, P.take)
ever touch them. Transition functions stay pure: state in, (state', out) out,
nothing mutated -- which is exactly why a Python model and a Clash .hs file
of the same block correspond line for line.

Run the examples:  python3 -m doctest clash.py -v
"""
import itertools
import prelude as P

# ---- constant and finite signals -------------------------------------------

pure = lambda x: P.repeat(x)                # Clash: pure 3 -- a constant signal
"""
>>> P.take(4, pure(3))
[3, 3, 3, 3]
"""

def fromList(xs, pad=None):
    """A finite test stimulus as a signal: xs, then `pad` forever
    (Clash's fromList errors off the end; simulations pad instead).
    >>> P.take(5, fromList([1, 2, 3], pad=0))
    [1, 2, 3, 0, 0]
    """
    yield from xs
    yield from P.repeat(xs[-1] if pad is None else pad)

# ---- the delay element -----------------------------------------------------

def register(init, sig):
    """One-tick delay: the flip-flop. Output at tick 0 is `init`; output at
    tick n+1 is the input at tick n.
    >>> P.take(4, register(0, fromList([7, 8, 9], pad=9)))
    [0, 7, 8, 9]
    """
    yield init
    yield from sig

# ---- state machines --------------------------------------------------------

def mealy(f, s0, inp):
    """Clash's mealy: f(state, input) -> (state', output), output may depend
    on the CURRENT input. The scanl pattern with the accumulator kept private.
    >>> acc = lambda s, i: (s + i, s + i)          # running sum
    >>> P.take(4, mealy(acc, 0, fromList([1, 2, 3, 4])))
    [1, 3, 6, 10]
    """
    s = s0
    for i in inp:
        s, o = f(s, i)
        yield o

def moore(f, g, s0, inp):
    """Clash's moore: output g(state) depends on STATE ONLY -- the input
    reaches the output one tick later than mealy. (This is why SantaGlide's
    gates are a moore machine: no combinational path from a pin to a MOSFET.)
    >>> acc = lambda s, i: s + i
    >>> P.take(4, moore(acc, P.id, 0, fromList([1, 2, 3, 4])))
    [0, 1, 3, 6]
    """
    s = s0
    for i in inp:
        yield g(s)
        s = f(s, i)

# ---- wiring ----------------------------------------------------------------

bundle = zip                                # (Signal a, Signal b) -> Signal (a, b)
"""
>>> P.take(2, bundle(pure(1), fromList('ab')))
[(1, 'a'), (1, 'b')]
"""

def unbundle(sig, n=2):
    """Signal of tuples -> tuple of signals. Needs tee: both halves must be
    consumable independently without re-running the source.
    >>> xs, ys = unbundle(fromList([(1, 'a'), (2, 'b')], pad=(0, '_')))
    >>> (P.take(2, xs), P.take(2, ys))
    ([1, 2], ['a', 'b'])
    """
    tees = itertools.tee(sig, n)
    return tuple(map(lambda k: (t[k] for t in tees[k]),  # noqa: B023
                     range(n)))

def fanout(sig, n=2):
    """One signal, several consumers. In Clash a Signal fans out for free
    (it is just a wire); a Python generator is single-shot, so fanning out
    NEEDS itertools.tee. Zipping a generator with itself instead interleaves
    odd/even samples -- the classic bug this combinator exists to prevent.
    >>> a, b = fanout(fromList([1, 2, 3], pad=0))
    >>> (P.take(3, a), P.take(3, b))
    ([1, 2, 3], [1, 2, 3])
    """
    import itertools as _it
    return _it.tee(sig, n)

sampleN = P.take                            # sampleN n sig -- the finite view
"""
>>> sampleN(3, pure('x'))
['x', 'x', 'x']
"""

if __name__ == "__main__":
    import doctest
    fails, total = doctest.testmod()
    print(f"clash.py doctests: {total - fails}/{total} pass")
