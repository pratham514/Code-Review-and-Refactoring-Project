"""Data classes shared by all layers.

REVIEW NOTE (R04, R13): the legacy script kept all state in module-level
globals and mixed calculation with printing. Plain data classes make the data
flow explicit and let every function be tested on its own.
"""
from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass(frozen=True)
class Order:
    """One valid row of the orders file."""
    order_id: str
    customer: str
    product: str
    category: str
    quantity: int
    unit_price: float
    order_date: date
    status: str

    @property
    def month(self) -> str:
        """Month key such as '2026-03' (used for the monthly report)."""
        return f"{self.order_date.year:04d}-{self.order_date.month:02d}"


@dataclass(frozen=True)
class PricedOrder:
    """An order together with its gross and net (after discount) amounts."""
    order: Order
    gross: float
    net: float


@dataclass(frozen=True)
class LoadResult:
    """Everything the loader found in a file."""
    orders: List[Order]
    cancelled: int
    invalid: int


@dataclass(frozen=True)
class Summary:
    """Headline numbers for the summary report."""
    processed: int
    cancelled: int
    invalid: int
    gross: float
    discounts: float
    net: float
