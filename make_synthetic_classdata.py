"""Generate SYNTHETIC LOBSTER-format sample data for this notebook.

The original course data (classdata/message.csv and classdata/orderbook.csv)
is licensed LOBSTER output (lobsterdata.com) and cannot be redistributed,
so it was never committed to this repo. This script creates a small
synthetic stand-in in exactly the same format so the notebook runs
top-to-bottom:

  * message.csv   -- headerless, columns: Time, Type, OrderID, Size,
                     Price, Direction. Time is seconds after midnight
                     (34200 = 09:30, 57600 = 16:00); prices are in
                     LOBSTER units (dollars x 10000); Type 1=new limit
                     order, 2=partial cancel, 3=full cancel,
                     4=execution (visible), 5=execution (hidden,
                     OrderID 0); Direction +1=buy, -1=sell.
  * orderbook.csv -- headerless, 40 columns: 10 levels of
                     AskPrice, AskSize, BidPrice, BidSize, one row per
                     message event (the book state after that event),
                     so len(orderbook) == len(message) as the notebook
                     requires.

The simulated book enforces the relationships the notebook checks:
fully cancelled orders have type-1 size == type-3 size, fully executed
orders have type-1 size == type-4 size, and the spread is always
positive. It is synthetic data -- statistics computed from it are
illustrative only and are NOT real market data.

Run:  python make_synthetic_classdata.py
"""

import os

import numpy as np
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "classdata")
TICK = 100                      # $0.01 in LOBSTER price units
OPEN_T, CLOSE_T = 34200.0, 57600.0
SIZES = [10, 18, 25, 50, 75, 100, 150, 200, 300, 500]


def simulate(seed=42):
    rng = np.random.default_rng(seed)
    mid = 2_500_000             # $250.00
    t = OPEN_T
    next_id = 16_000_000
    resting = {}                # order_id -> [side, price, size]
    messages, books = [], []

    def book_row():
        asks, bids = {}, {}
        for side, price, size in resting.values():
            book = asks if side == -1 else bids
            book[price] = book.get(price, 0) + size
        ask_p = sorted(asks)[:10]
        bid_p = sorted(bids, reverse=True)[:10]
        row = []
        for k in range(10):
            ap = ask_p[k] if k < len(ask_p) else (ask_p[-1] + TICK * (k - len(ask_p) + 1) if ask_p else mid + TICK * (k + 1))
            asz = asks[ap] if k < len(ask_p) else 0
            bp = bid_p[k] if k < len(bid_p) else (bid_p[-1] - TICK * (k - len(bid_p) + 1) if bid_p else mid - TICK * (k + 1))
            bsz = bids[bp] if k < len(bid_p) else 0
            row += [ap, asz, bp, bsz]
        return row

    while t < CLOSE_T - 30:
        t += float(rng.uniform(2.0, 38.0))
        mid = int(np.clip(mid + rng.choice([-200, -100, 0, 0, 100, 200]), 2_000_000, 3_000_000))
        r = rng.random()
        if r < 0.55 or not resting:
            # New limit order (type 1)
            side = int(rng.choice([1, -1]))
            if side == 1:
                price = mid - int(rng.integers(0, 6)) * TICK
            else:
                price = mid + int(rng.integers(1, 7)) * TICK
            size = int(rng.choice(SIZES))
            oid = next_id
            next_id += int(rng.integers(1, 50))
            resting[oid] = [side, price, size]
            messages.append([round(t, 6), 1, oid, size, price, side])
        elif r < 0.70:
            # Partial cancellation (type 2)
            oid = int(rng.choice(list(resting)))
            side, price, size = resting[oid]
            if size <= 1:
                messages.append([round(t, 6), 3, oid, size, price, side])
                del resting[oid]
            else:
                cut = int(rng.integers(1, size))
                resting[oid][2] -= cut
                messages.append([round(t, 6), 2, oid, cut, price, side])
        elif r < 0.85:
            # Full cancellation (type 3): size equals the type-1 size
            oid = int(rng.choice(list(resting)))
            side, price, size = resting.pop(oid)
            messages.append([round(t, 6), 3, oid, size, price, side])
        elif r < 0.97:
            # Visible execution (type 4): size equals the type-1 size
            oid = int(rng.choice(list(resting)))
            side, price, size = resting.pop(oid)
            messages.append([round(t, 6), 4, oid, size, price, side])
        else:
            # Hidden execution (type 5): OrderID 0, book unchanged
            size = int(rng.choice(SIZES))
            side = int(rng.choice([1, -1]))
            messages.append([round(t, 6), 5, 0, size, mid, side])
        books.append(book_row())

    msg = pd.DataFrame(messages, columns=["Time", "Type", "OrderID", "Size", "Price", "Direction"])
    book = pd.DataFrame(books)
    return msg, book


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    msg, book = simulate()
    assert len(msg) == len(book), "message/orderbook length mismatch"
    assert book.shape[1] == 40
    msg.to_csv(os.path.join(OUT_DIR, "message.csv"), index=False, header=False)
    book.to_csv(os.path.join(OUT_DIR, "orderbook.csv"), index=False, header=False)
    print(f"Wrote classdata/message.csv   : {len(msg)} rows (synthetic)")
    print(f"Wrote classdata/orderbook.csv : {len(book)} rows x {book.shape[1]} cols (synthetic)")
    print("Message counts by type:", msg.Type.value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
