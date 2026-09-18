"""logtriage.py -- 'LEVEL message' lines: error count, total, first error message."""
from haskell import foldMap, both, Sum, First, NOTHING, partial

# --- imperative ---
def triage_imp(lines):
    errors = 0                                        # three mutable slots
    total = 0
    first = None                                      # and a hand-rolled sentinel:
    seen_first = False                                # None alone can't mean "none yet"
    for ln in lines:                                  # if a message could be empty
        lvl, _, msg = ln.partition(' ')
        total += 1
        if lvl == 'ERROR':
            errors += 1
            if not seen_first:
                first, seen_first = msg, True
    return ((errors, total), first if seen_first else NOTHING)

# --- functional ---
tag = lambda ln: (lambda lvl, _, msg:
                  ((lvl == 'ERROR', 1), msg if lvl == 'ERROR' else NOTHING)
                  )(*ln.partition(' '))
triage_fn = partial(foldMap, tag, both(both(Sum, Sum), First))

# --- demo ---
if __name__ == "__main__":
    logs = ['INFO up', 'ERROR db down', 'WARN slow', 'ERROR retry', 'INFO ok']
    a, b = triage_imp(logs), triage_fn(logs)
    assert a == b, (a, b)
    print("triage:", b)
    assert triage_imp([])[1] is NOTHING and triage_fn([])[1] is NOTHING
    print("logtriage: both agree, empty log included")
