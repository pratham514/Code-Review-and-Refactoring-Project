"""Discount rules and order pricing.

REVIEW NOTE (R02, R03, R05, R11): in the legacy script this discount logic was
copy-pasted four times, and the copy in the "top customers" report forgot the
VIP bonus, so that report disagreed with the others. There is now exactly one
implementation, and every report uses it.
"""
from typing import Tuple

from .models import Order, PricedOrder

# Business rules as named constants instead of magic numbers (R05).
# Bulk tiers are (minimum quantity, discount rate), highest tier first.
BULK_TIERS: Tuple[Tuple[int, float], ...] = ((50, 0.15), (10, 0.10))
VIP_CUSTOMERS = frozenset({"alice", "bob"})
VIP_BONUS = 0.05
CATEGORY_BONUSES = {"electronics": 0.02}
MAX_DISCOUNT = 0.20


def bulk_rate(quantity: int) -> float:
    """Discount rate for the order size (0.0 below the smallest tier)."""
    for minimum, rate in BULK_TIERS:
        if quantity >= minimum:
            return rate
    return 0.0


def discount_rate(quantity: int, customer: str, category: str) -> float:
    """Total discount rate: bulk + VIP bonus + category bonus, capped at MAX_DISCOUNT."""
    rate = bulk_rate(quantity)
    if customer.lower() in VIP_CUSTOMERS:
        rate += VIP_BONUS
    rate += CATEGORY_BONUSES.get(category.lower(), 0.0)
    return min(rate, MAX_DISCOUNT)


def price_order(order: Order) -> PricedOrder:
    """Calculate gross and net amounts. Net is rounded to 2 decimals per order."""
    gross = order.quantity * order.unit_price
    rate = discount_rate(order.quantity, order.customer, order.category)
    net = round(gross * (1 - rate), 2)
    return PricedOrder(order, gross, net)
