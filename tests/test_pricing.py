"""Unit tests for the discount rules."""
import unittest
from datetime import date

from helpers import ROOT  # noqa: F401  (puts the project root on sys.path)
from salesreport.models import Order
from salesreport.pricing import bulk_rate, discount_rate, price_order


def make_order(quantity=1, price=100.0, customer="zed", category="home"):
    return Order("1", customer, "thing", category, quantity, price, date(2026, 1, 1), "completed")


class BulkRateTests(unittest.TestCase):
    def test_tier_boundaries(self):
        self.assertEqual(bulk_rate(9), 0.0)
        self.assertEqual(bulk_rate(10), 0.10)
        self.assertEqual(bulk_rate(49), 0.10)
        self.assertEqual(bulk_rate(50), 0.15)
        self.assertEqual(bulk_rate(500), 0.15)

    def test_small_and_zero_quantities(self):
        self.assertEqual(bulk_rate(0), 0.0)
        self.assertEqual(bulk_rate(1), 0.0)


class DiscountRateTests(unittest.TestCase):
    def test_no_discount_for_small_regular_order(self):
        self.assertEqual(discount_rate(1, "zed", "home"), 0.0)

    def test_vip_bonus_is_case_insensitive(self):
        self.assertEqual(discount_rate(1, "ALICE", "home"), 0.05)
        self.assertEqual(discount_rate(1, "bob", "home"), 0.05)

    def test_electronics_bonus_is_case_insensitive(self):
        self.assertEqual(discount_rate(1, "zed", "Electronics"), 0.02)

    def test_rates_add_up(self):
        self.assertAlmostEqual(discount_rate(10, "alice", "electronics"), 0.17)

    def test_total_is_capped_at_twenty_percent(self):
        self.assertEqual(discount_rate(50, "alice", "electronics"), 0.20)   # 0.22 before cap


class PriceOrderTests(unittest.TestCase):
    def test_gross_and_net_without_discount(self):
        priced = price_order(make_order(quantity=2, price=50.0))
        self.assertEqual(priced.gross, 100.0)
        self.assertEqual(priced.net, 100.0)

    def test_net_is_rounded_to_two_decimals(self):
        priced = price_order(make_order(quantity=2, price=899.99, customer="dave", category="electronics"))
        self.assertEqual(priced.gross, 1799.98)
        self.assertEqual(priced.net, 1763.98)          # 1799.98 * 0.98 = 1763.9804

    def test_worked_example_from_the_report(self):
        # 12 x 210.00 for VIP Alice buying electronics: 10% + 5% + 2% = 17% off
        priced = price_order(make_order(quantity=12, price=210.0, customer="Alice", category="Electronics"))
        self.assertEqual(priced.net, 2091.60)


if __name__ == "__main__":
    unittest.main()
