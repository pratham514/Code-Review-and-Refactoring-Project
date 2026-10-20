"""Turn report results into text. No calculations happen here."""
from typing import List, Tuple

from .models import Summary

LABEL_WIDTH = 16


def format_summary(summary: Summary) -> str:
    """The headline numbers block."""
    return "\n".join([
        "== Summary ==",
        f"Orders processed: {summary.processed}",
        f"Cancelled skipped: {summary.cancelled}",
        f"Invalid rows skipped: {summary.invalid}",
        f"Gross revenue: {summary.gross:.2f}",
        f"Total discounts: {summary.discounts:.2f}",
        f"Net revenue: {summary.net:.2f}",
    ]) + "\n"


def _format_table(title: str, rows: List[Tuple[str, float]]) -> str:
    """Title line followed by one aligned (label, amount) line per row."""
    lines = [title]
    lines.extend(f"{label:<{LABEL_WIDTH}}{amount:>10.2f}" for label, amount in rows)
    return "\n".join(lines) + "\n"


def format_categories(rows: List[Tuple[str, float]]) -> str:
    """Revenue-by-category table."""
    return _format_table("== Revenue by category ==", rows)


def format_months(rows: List[Tuple[str, float]]) -> str:
    """Monthly revenue table."""
    return _format_table("== Monthly revenue ==", rows)


def format_top_customers(rows: List[Tuple[str, float]], limit: int) -> str:
    """`limit` is the report size, shown in the title even if fewer customers exist."""
    lines = [f"== Top {limit} customers =="]
    lines.extend(f"{rank}. {name:<{LABEL_WIDTH}}{amount:>10.2f}"
                 for rank, (name, amount) in enumerate(rows, start=1))
    return "\n".join(lines) + "\n"
