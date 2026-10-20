"""CSV loading and validation.

REVIEW NOTE (R01, R06, R07): the legacy loader was one long function that
parsed, validated, priced and aggregated, caught every error with a bare
``except:`` and closed the file by hand. Parsing is now a small function that
raises a specific error, and the file is opened with ``with``.
"""
import csv
from datetime import datetime
from typing import List

from .models import LoadResult, Order

DATE_FORMAT = "%Y-%m-%d"
COLUMN_COUNT = 8          # order_id, customer, product, category, quantity, unit_price, date, status
CANCELLED_STATUS = "cancelled"


class InvalidRowError(ValueError):
    """Raised when a CSV row cannot be turned into an Order."""


def parse_row(row: List[str]) -> Order:
    """Convert one CSV row into an Order, or raise InvalidRowError."""
    if len(row) < COLUMN_COUNT:
        raise InvalidRowError(f"expected {COLUMN_COUNT} columns, got {len(row)}")
    order_id, customer, product, category, quantity, unit_price, order_date, status = row[:COLUMN_COUNT]
    try:
        return Order(
            order_id=order_id,
            customer=customer,
            product=product,
            category=category,
            quantity=int(quantity),
            unit_price=float(unit_price),
            order_date=datetime.strptime(order_date, DATE_FORMAT).date(),
            status=status,
        )
    except ValueError as err:      # int(), float() and strptime() all raise ValueError
        raise InvalidRowError(str(err)) from err


def is_cancelled(order: Order) -> bool:
    """True for orders whose status is 'cancelled' (any capitalisation)."""
    return order.status.strip().lower() == CANCELLED_STATUS


def load_orders(path: str) -> LoadResult:
    """Read an orders CSV. The first row is a header and is skipped.

    Cancelled orders are counted but not returned; unreadable rows are counted
    as invalid. A row is validated BEFORE the cancelled check, exactly as the
    legacy script did (a cancelled row with a bad date counts as invalid).
    """
    orders: List[Order] = []
    cancelled = 0
    invalid = 0
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        next(reader, None)                      # skip header
        for row in reader:
            try:
                order = parse_row(row)
            except InvalidRowError:
                invalid += 1
                continue
            if is_cancelled(order):
                cancelled += 1
            else:
                orders.append(order)
    return LoadResult(orders, cancelled, invalid)
