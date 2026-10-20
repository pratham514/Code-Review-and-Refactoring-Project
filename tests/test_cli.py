"""Tests for the command-line layer (run in-process so coverage can see them)."""
import contextlib
import io
import unittest

from helpers import SAMPLE, split_sections  # noqa: F401
from salesreport.cli import build_report, main


class BuildReportTests(unittest.TestCase):
    def test_report_has_four_sections_in_order(self):
        titles = [line for line in build_report(SAMPLE).splitlines() if line.startswith("== ")]
        self.assertEqual(titles, ["== Summary ==", "== Revenue by category ==",
                                  "== Top 3 customers ==", "== Monthly revenue =="])

    def test_summary_numbers_for_the_sample_file(self):
        summary = split_sections(build_report(SAMPLE))["== Summary =="]
        self.assertIn("Orders processed: 18", summary)
        self.assertIn("Cancelled skipped: 2", summary)
        self.assertIn("Invalid rows skipped: 4", summary)
        self.assertIn("Net revenue: 13044.35", summary)


class MainTests(unittest.TestCase):
    def test_success_returns_zero_and_prints_report(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = main([SAMPLE])
        self.assertEqual(code, 0)
        self.assertIn("== Summary ==", out.getvalue())

    def test_missing_file_returns_two_with_friendly_message(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = main(["definitely_missing.csv"])
        self.assertEqual(code, 2)
        self.assertIn("cannot read 'definitely_missing.csv'", err.getvalue())


if __name__ == "__main__":
    unittest.main()
