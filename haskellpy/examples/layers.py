"""layers.py -- layered config: defaults < file < cli; None is a real value."""
from haskell import NOTHING, maybe_get, mconcat, Last, unionWith, foldl, fromMaybe

DEFAULTS = {'host': 'localhost', 'port': 8080, 'proxy': 'corp'}
FILECFG  = {'port': 9000, 'proxy': None}      # file EXPLICITLY disables the proxy
CLI      = {'host': '10.0.0.1'}
LAYERS   = [DEFAULTS, FILECFG, CLI]

# --- imperative ---
_UNSET = object()                                     # invent a private sentinel,
def effective_imp(layers, k):                         # because None must survive
    val = _UNSET
    for d in layers:
        if k in d:
            val = d[k]
    return NOTHING if val is _UNSET else val

def merged_imp(layers):
    out = {}
    for d in layers:
        for k, v in d.items():
            out[k] = v
    return out

# --- functional ---
effective_fn = lambda layers, k: mconcat(Last, [maybe_get(d, k) for d in layers])
merged_fn    = lambda layers: foldl(lambda a, b: unionWith(lambda old, new: new, a, b),
                                    layers, {})

# --- demo ---
if __name__ == "__main__":
    for k in ['host', 'port', 'proxy', 'nope']:
        a, b = effective_imp(LAYERS, k), effective_fn(LAYERS, k)
        assert a is b or a == b, (k, a, b)
        print(f"{k:6s} -> {b!r}")
    assert merged_imp(LAYERS) == merged_fn(LAYERS)
    assert effective_fn(LAYERS, 'proxy') is None      # the disable survives
    print("layers: both agree; explicit None beat the default")
