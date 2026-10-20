"""Unit tests for CSV loading and validation."""
import os
import tempfile
import unittest

from helpers import ROOT, SAMPLE  # noqa: F401
from salesreport.loader import InvalidRowError, is_cancelled, load_orders, parse_row

HEADER = "order_id,customer,product,category,quantity,unit_price,date,status\n"


def write_temp(text):
    handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
    handle.write(text)
    handle.close()
    return handle.name


class ParseRowTests(unittest.TestCase):
    GOOD = ["1", "Alice", "Pen", "Home", "3", "2.50", "2026-02-03", "completed"]

    def test_valid_row(self):
        order = parse_row(self.GOOD)
        self.assertEqual((order.customer, order.quantity, order.unit_price), ("Alice", 3, 2.5))
        self.assertEqual(order.month, "2026-02")

    def test_bad_quantity(self):
        with self.assertRaises(InvalidRowError):
            parse_row(self.GOOD[:4] + ["x"] + self.GOOD[5:])

    def test_bad_price(self):
        with self.assertRaises(InvalidRowError):
            parse_row(self.GOOD[:5] + ["abc"] + self.GOOD[6:])

    def test_impossible_date(self):
        with self.assertRaises(InvalidRowError):
            parse_row(self.GOOD[:6] + ["2026-02-30", "completed"])

    def test_wrong_date_format(self):
        with self.assertRaises(InvalidRowError):
            parse_row(self.GOOD[:6] + ["05/02/2026", "completed"])

    def test_short_row(self):
        with self.assertRaises(InvalidRowError):
            parse_row(self.GOOD[:7])

    def test_non_padded_date_is_accepted_and_month_is_normalised(self):    # review finding R19
        order = parse_row(self.GOOD[:6] + ["2026-3-5", "completed"])
        self.assertEqual(order.month, "2026-03")

    def test_extra_columns_are_ignored(self):
        self.assertEqual(parse_row(self.GOOD + ["extra"]).order_id, "1")


class IsCancelledTests(unittest.TestCase):
    def test_any_capitalisation_and_spaces(self):
        base = parse_row(ParseRowTests.GOOD)
        for status in ("cancelled", "Cancelled", " CANCELLED "):
            self.assertTrue(is_cancelled(type(base)(**{**base.__dict__, "status": status})))

    def test_other_statuses_are_not_cancelled(self):
        base = parse_row(ParseRowTests.GOOD)
        self.assertFalse(is_cancelled(base))


class LoadOrdersTests(unittest.TestCase):
    def test_header_is_skipped_and_counts_are_correct(self):
        path = write_temp(HEADER +
                          "1,a,p,home,1,5.0,2026-01-01,completed\n"
                          "2,b,p,home,1,5.0,2026-01-01,cancelled\n"
                          "3,c,p,home,zz,5.0,2026-01-01,completed\n")
        result = load_orders(path)
        os.unlink(path)
        self.assertEqual((len(result.orders), result.cancelled, result.invalid), (1, 1, 1))

    def test_cancelled_row_with_bad_date_counts_as_invalid(self):
        path = write_temp(HEADER + "1,a,p,home,1,5.0,not-a-date,cancelled\n")
        result = load_orders(path)
        os.unlink(path)
        self.assertEqual((len(result.orders), result.cancelled, result.invalid), (0, 0, 1))

    def test_header_only_file(self):
        path = write_temp(HEADER)
        result = load_orders(path)
        os.unlink(path)
        self.assertEqual((len(result.orders), result.cancelled, result.invalid), (0, 0, 0))

    def test_empty_file(self):
        path = write_temp("")
        result = load_orders(path)
        os.unlink(path)
        self.assertEqual(len(result.orders), 0)

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_orders(os.path.join(ROOT, "no_such_file.csv"))

    def test_sample_file_counts(self):
        result = load_orders(SAMPLE)
        self.assertEqual((len(result.orders), result.cancelled, result.invalid), (18, 2, 4))


if __name__ == "__main__":
    unittest.main()
