"""Profile the legacy script with cProfile to find where the time goes.

Usage: python tools/profile_legacy.py
"""
import cProfile
import importlib.util
import io
import os
import pstats
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.generate_orders import write_csv  # noqa: E402


def main():
    spec = importlib.util.spec_from_file_location("sales_report", os.path.join(ROOT, "legacy", "sales_report.py"))
    legacy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(legacy)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "orders.csv")
        write_csv(path, rows=20000, customers=2000, seed=5)

        def run():
            legacy.process(path)
            legacy.summary(), legacy.cat_report(), legacy.top_report(), legacy.monthly_report()

        profiler = cProfile.Profile()
        profiler.runcall(run)
    stream = io.StringIO()
    pstats.Stats(profiler, stream=stream).sort_stats("cumulative").print_stats(8)
    print("\n".join(line.rstrip() for line in stream.getvalue().splitlines() if line.strip()))


if __name__ == "__main__":
    main()
