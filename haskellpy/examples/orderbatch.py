"""orderbatch.py -- capstone: validate a batch of orders (qty > 0, price > 0),
computing each line total; the whole batch fails at the first bad order,
carrying which one and why."""
from haskell import Ok, Err, bindE, sequenceE, doE

ORDERS_OK = [{"item": "pen", "qty": 3, "price": 1.5},
             {"item": "cup", "qty": 2, "price": 4.0}]
ORDERS_BAD = [{"item": "pen", "qty": 3, "price": 1.5},
              {"item": "cup", "qty": 0, "price": 4.0}]

# --- imperative ---
def total_imp(order):
    if order["qty"] <= 0:
        return ("err", f"{order['item']}: bad qty {order['qty']}")
    if order["price"] <= 0:
        return ("err", f"{order['item']}: bad price {order['price']}")
    return ("ok", round(order["qty"] * order["price"], 2))

def admit_imp(orders):
    out = []
    for o in orders:
        r = total_imp(o)
        if r[0] == "err":
            return r
        out.append(r[1])
    return ("ok", out)

# --- functional ---
@doE
def total_fn(order):
    qty = yield (Ok(order["qty"]) if order["qty"] > 0
                 else Err(f"{order['item']}: bad qty {order['qty']}"))
    price = yield (Ok(order["price"]) if order["price"] > 0
                   else Err(f"{order['item']}: bad price {order['price']}"))
    return Ok(round(qty * price, 2))

admit_fn = lambda orders: sequenceE([total_fn(o) for o in orders])

# --- demo ---
if __name__ == "__main__":
    for orders in (ORDERS_OK, ORDERS_BAD):
        a, b = admit_imp(orders), admit_fn(orders)
        assert a == b, (a, b)
    print("good batch:", admit_fn(ORDERS_OK))
    print("bad batch: ", admit_fn(ORDERS_BAD))
    print("orderbatch: both agree")
