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

# --- oop ---
class Player:
    def __init__(self, name, score):
        self.name = name
        self.score = max(0, min(100, score))          # clamp at construction time

class Leaderboard:
    def __init__(self):
        self.players = []

    def add(self, name, score):
        self.players.append(Player(name, score))
        return self

    def ranked(self):
        ordered = sorted(self.players, key=lambda p: (-p.score, p.name))
        return [(p.name, p.score) for p in ordered]

def rank_oop(rows):
    board = Leaderboard()
    for name, score in rows:
        board.add(name, score)
    return board.ranked()

# --- demo ---
if __name__ == "__main__":
    a, b, c = rank_imp(ROWS), rank_fn(ROWS), rank_oop(ROWS)
    assert a == b == c, (a, b, c)
    print("ranked:", b)
    print("leaderboard: all three agree")
