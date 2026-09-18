"""leaderboard.py -- clamp scores into [0, 100], rank by score desc, name asc."""
from haskell import o, partial, sortOn
from operator import itemgetter

ROWS = [("ada", 130), ("bob", -5), ("cy", 82), ("dee", 82), ("ed", 47)]

# --- imperative ---
def rank_imp(rows):
    clamped = []
    for name, score in rows:
        if score < 0:
            score = 0
        elif score > 100:
            score = 100
        clamped.append((name, score))
    clamped.sort(key=lambda r: (-r[1], r[0]))          # score desc, name asc
    return clamped

# --- functional ---
clamp = lambda lo, hi: o(partial(max, lo), partial(min, hi))
clamp100 = clamp(0, 100)
name_of, score_of = itemgetter(0), itemgetter(1)
rank_fn = lambda rows: sortOn(
    lambda r: (-score_of(r), name_of(r)),
    [(name_of(r), clamp100(score_of(r))) for r in rows])

# --- demo ---
if __name__ == "__main__":
    a, b = rank_imp(ROWS), rank_fn(ROWS)
    assert a == b, (a, b)
    print("ranked:", b)
    print("leaderboard: both agree")
