"""End-to-end timing: legacy script vs refactored program.

Usage: python tools/benchmark.py
Generates reproducible data files, then runs each program as a separate
process (best of 3) so start-up cost is included for both.
"""
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.generate_orders import write_csv  # noqa: E402

SIZES = [(2000, 200), (10000, 1000), (20000, 2000)]   # (rows, customers)


def best_time(command, runs=3):
    best = None
    for _ in range(runs):
        start = time.perf_counter()
        subprocess.run(command, cwd=ROOT, stdout=subprocess.DEVNULL, check=True)
        elapsed = time.perf_counter() - start
        best = elapsed if best is None else min(best, elapsed)
    return best


def main():
    print(f"{'Rows':>7}{'Customers':>11}{'Before (s)':>13}{'After (s)':>12}{'Speed-up':>11}")
    for rows, customers in SIZES:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "orders.csv")
            write_csv(path, rows=rows, customers=customers, seed=5)
            old = best_time([sys.executable, os.path.join(ROOT, "legacy", "sales_report.py"), path])
            new = best_time([sys.executable, "-m", "salesreport", path])
        print(f"{rows:>7}{customers:>11}{old:>13.3f}{new:>12.3f}{old / new:>10.1f}x")


if __name__ == "__main__":
    main()
