"""Command-line entry point.

Usage:  python -m salesreport [orders.csv]
"""
import argparse
import sys
from typing import List, Optional

from .formatting import (format_categories, format_months, format_summary,
                         format_top_customers)
from .loader import load_orders
from .reports import (TOP_CUSTOMER_COUNT, price_all, revenue_by_category,
                      revenue_by_month, summarize, top_customers)

DEFAULT_FILE = "orders.csv"


def build_report(path: str) -> str:
    """Load the file and return the complete report text."""
    loaded = load_orders(path)
    priced = price_all(loaded)
    sections = [
        format_summary(summarize(priced, loaded.cancelled, loaded.invalid)),
        format_categories(revenue_by_category(priced)),
        format_top_customers(top_customers(priced), TOP_CUSTOMER_COUNT),
        format_months(revenue_by_month(priced)),
    ]
    return "\n".join(sections)


def main(argv: Optional[List[str]] = None) -> int:
    """Run the program. Returns the process exit code (0 = ok, 2 = file problem)."""
    parser = argparse.ArgumentParser(description="Print sales reports from an orders CSV file.")
    parser.add_argument("csv_path", nargs="?", default=DEFAULT_FILE,
                        help=f"orders file (default: {DEFAULT_FILE})")
    args = parser.parse_args(argv)
    try:
        print(build_report(args.csv_path))
    except OSError as err:
        print(f"error: cannot read '{args.csv_path}': {err.strerror}", file=sys.stderr)
        return 2
    return 0
