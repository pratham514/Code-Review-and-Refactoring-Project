"""Unit tests for the report calculations and formatting."""
import unittest
from datetime import date

from helpers import ROOT  # noqa: F401
from salesreport.formatting import (format_categories, format_months, format_summary,
                                    format_top_customers)
from salesreport.models import LoadResult, Order, PricedOrder
from salesreport.reports import (price_all, revenue_by_category, revenue_by_month,
                                 summarize, top_customers)


def line(customer, category, month, net, gross=None):
    order = Order("1", customer, "p", category, 1, net, date(2026, month, 1), "completed")
    return PricedOrder(order, net if gross is None else gross, net)


class SummaryTests(unittest.TestCase):
    def test_totals(self):
        priced = [line("a", "home", 1, 90.0, gross=100.0), line("b", "home", 1, 50.0)]
        s = summarize(priced, cancelled=2, invalid=3)
        self.assertEqual((s.processed, s.cancelled, s.invalid), (2, 2, 3))
        self.assertEqual((s.gross, s.discounts, s.net), (150.0, 10.0, 140.0))

    def test_empty(self):
        s = summarize([], 0, 0)
        self.assertEqual((s.processed, s.gross, s.net), (0, 0, 0))

    def test_summary_text(self):
        text = format_summary(summarize([line("a", "home", 1, 10.0)], 1, 2))
        self.assertEqual(text.splitlines()[0], "== Summary ==")
        self.assertIn("Cancelled skipped: 1", text)
        self.assertIn("Net revenue: 10.00", text)


class PriceAllTests(unittest.TestCase):
    def test_every_order_is_priced_once(self):
        order = Order("1", "alice", "p", "electronics", 12, 210.0, date(2026, 1, 1), "completed")
        priced = price_all(LoadResult([order, order], 0, 0))
        self.assertEqual([p.net for p in priced], [2091.60, 2091.60])


class GroupingTests(unittest.TestCase):
    def setUp(self):
        self.priced = [line("a", "Home", 3, 10.0), line("b", "home", 1, 30.0),
                       line("c", "Toys", 1, 20.0), line("a", "toys", 2, 5.0)]

    def test_categories_are_merged_case_insensitively_and_sorted_desc(self):
        self.assertEqual(revenue_by_category(self.priced), [("home", 40.0), ("toys", 25.0)])

    def test_months_are_in_calendar_order(self):
        self.assertEqual(revenue_by_month(self.priced),
                         [("2026-01", 50.0), ("2026-02", 5.0), ("2026-03", 10.0)])

    def test_ties_keep_first_appearance_order(self):
        tied = [line("x", "b", 1, 10.0), line("y", "a", 1, 10.0)]
        self.assertEqual([name for name, _ in revenue_by_category(tied)], ["b", "a"])

    def test_empty_input(self):
        self.assertEqual(revenue_by_category([]), [])
        self.assertEqual(revenue_by_month([]), [])
        self.assertEqual(top_customers([]), [])


class TopCustomerTests(unittest.TestCase):
    def test_only_the_limit_is_returned_highest_first(self):
        priced = [line(n, "home", 1, v) for n, v in
                  [("a", 5.0), ("b", 50.0), ("c", 20.0), ("d", 40.0), ("e", 1.0)]]
        self.assertEqual(top_customers(priced), [("b", 50.0), ("d", 40.0), ("c", 20.0)])

    def test_customer_names_are_merged_case_insensitively(self):
        priced = [line("Alice", "home", 1, 10.0), line("ALICE", "home", 1, 5.0)]
        self.assertEqual(top_customers(priced), [("alice", 15.0)])

    def test_fewer_customers_than_limit(self):
        self.assertEqual(len(top_customers([line("a", "home", 1, 1.0)])), 1)


class FormattingTests(unittest.TestCase):
    def test_category_table_layout(self):
        text = format_categories([("home", 40.0)])
        expected = "== Revenue by category ==\n" + "home".ljust(16) + "40.00".rjust(10) + "\n"
        self.assertEqual(text, expected)

    def test_month_table_layout(self):
        expected = "== Monthly revenue ==\n" + "2026-01".ljust(16) + "1.50".rjust(10) + "\n"
        self.assertEqual(format_months([("2026-01", 1.5)]), expected)

    def test_top_customers_layout_and_fixed_title(self):
        text = format_top_customers([("alice", 12.0)], 3)
        expected = "== Top 3 customers ==\n1. " + "alice".ljust(16) + "12.00".rjust(10) + "\n"
        self.assertEqual(text, expected)


if __name__ == "__main__":
    unittest.main()
