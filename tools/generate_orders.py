"""Generate a reproducible orders CSV for tests and benchmarks.

Usage: python tools/generate_orders.py OUTPUT.csv [rows] [customers] [seed]
"""
import csv
import random
import sys
from datetime import date, timedelta

CATEGORIES = ["Electronics", "Home", "Stationery", "Travel", "Garden", "Toys", "Books", "Sports"]
STATUSES = ["completed", "completed", "completed", "completed", "refunded", "cancelled"]
HEADER = ["order_id", "customer", "product", "category", "quantity", "unit_price", "date", "status"]


def generate_rows(rows=1000, customers=100, seed=1, include_vips=True):
    """Return a list of CSV rows (header first). About 3% of rows are invalid."""
    rng = random.Random(seed)
    names = [f"cust{i:04d}" for i in range(customers)]
    if include_vips:
        names += ["Alice", "Bob"]
    start = date(2025, 1, 1)
    out = [HEADER]
    for order_id in range(1, rows + 1):
        day = start + timedelta(days=rng.randrange(0, 600))
        quantity = rng.choice([1, 1, 2, 3, 5, 8, 10, 12, 25, 50, 80])
        row = [order_id, rng.choice(names), f"product{rng.randrange(40)}", rng.choice(CATEGORIES),
               quantity, f"{rng.uniform(1, 500):.2f}", day.isoformat(), rng.choice(STATUSES)]
        roll = rng.random()
        if roll < 0.01:
            row[5] = "n/a"            # bad price
        elif roll < 0.02:
            row[6] = "2025-13-40"     # bad date
        elif roll < 0.03:
            row = row[:6]             # short row
        out.append(row)
    return out


def write_csv(path, **kwargs):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        csv.writer(handle).writerows(generate_rows(**kwargs))


if __name__ == "__main__":
    target = sys.argv[1]
    n_rows = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    n_customers = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    seed_value = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    write_csv(target, rows=n_rows, customers=n_customers, seed=seed_value)
    print(f"wrote {n_rows} rows to {target}")
