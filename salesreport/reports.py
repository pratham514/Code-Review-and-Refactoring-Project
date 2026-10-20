"""Report calculations. Pure functions: no printing, no files, no globals.

REVIEW NOTE (R09, R10, R11): the legacy reports re-priced every order and
looked up groups by scanning a list (O(n x groups)), then sorted with a
hand-written bubble sort. Here each order is priced once and totals are kept
in dictionaries (O(1) lookup); sorting uses sorted()/heapq, which are stable,
so ties keep the same order as before.
"""
import heapq
from typing import Dict, Iterable, List, Tuple

from .models import LoadResult, PricedOrder, Summary
from .pricing import price_order

TOP_CUSTOMER_COUNT = 3


def price_all(load_result: LoadResult) -> List[PricedOrder]:
    """Price every order exactly once."""
    return [price_order(order) for order in load_result.orders]


def summarize(priced: Iterable[PricedOrder], cancelled: int, invalid: int) -> Summary:
    """Headline totals."""
    count = 0
    gross = 0
    discounts = 0
    net = 0
    for item in priced:
        count += 1
        gross += item.gross
        discounts += item.gross - item.net
        net += item.net
    return Summary(count, cancelled, invalid, gross, discounts, net)


def _totals_by(priced: Iterable[PricedOrder], key) -> Dict[str, float]:
    """Sum net amounts per key, keeping first-appearance order."""
    totals: Dict[str, float] = {}
    for item in priced:
        group = key(item)
        totals[group] = totals.get(group, 0) + item.net
    return totals


def revenue_by_category(priced: Iterable[PricedOrder]) -> List[Tuple[str, float]]:
    """(category, net revenue) pairs, highest revenue first."""
    totals = _totals_by(priced, lambda p: p.order.category.lower())
    return sorted(totals.items(), key=lambda pair: pair[1], reverse=True)


def revenue_by_month(priced: Iterable[PricedOrder]) -> List[Tuple[str, float]]:
    """(month, net revenue) pairs in calendar order."""
    totals = _totals_by(priced, lambda p: p.order.month)
    return sorted(totals.items())


def top_customers(priced: Iterable[PricedOrder],
                  limit: int = TOP_CUSTOMER_COUNT) -> List[Tuple[str, float]]:
    """The `limit` customers with the highest net spend (names lower-cased)."""
    totals = _totals_by(priced, lambda p: p.order.customer.lower())
    return heapq.nlargest(limit, totals.items(), key=lambda pair: pair[1])
