"""Shows two defects of the legacy script that were found during the review.

R04: global state - processing a file twice doubles every number.
R19: a date such as 2026-3-5 passes validation but produces a broken month label.

Usage: python tools/demo_legacy_defects.py
"""
import importlib.util
import os
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE = os.path.join(ROOT, "data", "sample_orders.csv")


def load_legacy():
    spec = importlib.util.spec_from_file_location("sales_report", os.path.join(ROOT, "legacy", "sales_report.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


print("--- R04: processing the same file twice (legacy) ---")
legacy = load_legacy()
legacy.process(SAMPLE)
legacy.process(SAMPLE)
print("\n".join(legacy.summary().splitlines()[:3]))

print("\n--- R19: non-zero-padded date (legacy monthly report) ---")
legacy = load_legacy()
with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as handle:
    handle.write("order_id,customer,product,category,quantity,unit_price,date,status\n")
    handle.write("1,zed,pen,home,1,10.00,2026-3-5,completed\n")
path = handle.name
legacy.process(path)
os.unlink(path)
print(legacy.monthly_report())
