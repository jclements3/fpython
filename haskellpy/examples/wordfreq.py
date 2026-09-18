"""wordfreq.py -- top-N word frequencies, ties alphabetical."""
from haskell import pipe, words, fromListWith, add, sortOn, take, partial

TEXT = "the quick brown fox jumps over the lazy dog the fox"

# --- imperative ---
def top_imp(n, text):
    counts = {}                                       # mutate a dict
    for w in text.lower().split():
        if w in counts:
            counts[w] += 1
        else:
            counts[w] = 1
    items = list(counts.items())                      # then sort, then slice
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items[:n]

# --- functional ---
top_fn = lambda n, text: pipe(
    text, str.lower, words,
    lambda ws: fromListWith(add, [(w, 1) for w in ws]),
    dict.items, partial(sortOn, lambda kv: (-kv[1], kv[0])),
    partial(take, n))

# --- demo ---
if __name__ == "__main__":
    a, b = top_imp(3, TEXT), top_fn(3, TEXT)
    assert a == b, (a, b)
    print("top 3:", b)
    print("wordfreq: both agree")
