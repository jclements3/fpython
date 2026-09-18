"""payoff.py -- loan payoff schedule: balances after each fixed payment,
and how many payments until paid off."""
from haskell import unfoldr, NOTHING

# --- imperative ---
def schedule_imp(balance, payment, rate):
    out, n = [balance], 0
    while balance > 0:
        balance = round(balance * (1 + rate) - payment, 2)
        if balance < 0:
            balance = 0.0
        out.append(balance)
        n += 1
    return out, n

# --- functional ---
def _step(payment, rate):
    def step(balance):
        if balance <= 0:
            return NOTHING
        nxt = round(balance * (1 + rate) - payment, 2)
        nxt = max(nxt, 0.0)
        return (nxt, nxt)
    return step

def schedule_fn(balance, payment, rate):
    rest = unfoldr(_step(payment, rate), balance)
    return [balance] + rest, len(rest)

# --- demo ---
if __name__ == "__main__":
    a, b = schedule_imp(1000, 120, 0.02), schedule_fn(1000, 120, 0.02)
    assert a == b, (a, b)
    hist, n = b
    print(f"paid off in {n} payments:", hist)
    print("payoff: both agree")
