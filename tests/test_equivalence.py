"""Characterisation (regression) tests: the refactored program must print the
same reports as the legacy script.

The ONLY intentional difference is review finding R03: the legacy "top
customers" report ignored the VIP discount. When no VIP customer is present
the two programs must produce byte-identical output.
"""
import os
import tempfile
import unittest

from helpers import SAMPLE, run_legacy, run_new, split_sections
from tools.generate_orders import write_csv

SAME = ["== Summary ==", "== Revenue by category ==", "== Monthly revenue =="]
TOP = "== Top 3 customers =="


class SampleFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = split_sections(run_legacy(SAMPLE))
        cls.new = split_sections(run_new(SAMPLE))

    def test_summary_category_and_monthly_reports_are_identical(self):
        for title in SAME:
            self.assertEqual(self.old[title], self.new[title], title)

    def test_top_customers_differ_only_by_the_vip_fix(self):
        old_lines = self.old[TOP].splitlines()
        new_lines = self.new[TOP].splitlines()
        self.assertIn("1. alice              9293.58", old_lines)    # legacy: VIP discount missing
        self.assertIn("1. alice              8885.58", new_lines)    # fixed:  17%/22%->20% discounts
        self.assertEqual(old_lines[2:], new_lines[2:])               # other ranks unchanged


class GeneratedFileTests(unittest.TestCase):
    def run_pair(self, **kwargs):
        handle = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        handle.close()
        try:
            write_csv(handle.name, **kwargs)
            return run_legacy(handle.name), run_new(handle.name)
        finally:
            os.unlink(handle.name)

    def test_without_vip_customers_output_is_byte_identical(self):
        old, new = self.run_pair(rows=3000, customers=250, seed=7, include_vips=False)
        self.assertEqual(old, new)

    def test_with_vip_customers_three_reports_are_identical(self):
        old, new = self.run_pair(rows=3000, customers=250, seed=11, include_vips=True)
        old_sections, new_sections = split_sections(old), split_sections(new)
        for title in SAME:
            self.assertEqual(old_sections[title], new_sections[title], title)


if __name__ == "__main__":
    unittest.main()
