"""Shared test helpers."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

SAMPLE = os.path.join(ROOT, "data", "sample_orders.csv")
LEGACY = os.path.join(ROOT, "legacy", "sales_report.py")


def run_legacy(csv_path):
    """Run the original script and return its stdout."""
    return subprocess.run([sys.executable, LEGACY, csv_path], capture_output=True,
                          text=True, check=True, cwd=ROOT).stdout


def run_new(csv_path):
    """Run the refactored program and return its stdout."""
    return subprocess.run([sys.executable, "-m", "salesreport", csv_path], capture_output=True,
                          text=True, check=True, cwd=ROOT).stdout


def split_sections(text):
    """Split report text into {title: body} using the '== Title ==' lines."""
    sections, title, body = {}, None, []
    for line in text.splitlines():
        if line.startswith("== "):
            if title:
                sections[title] = "\n".join(body).strip()
            title, body = line, [line]
        elif title:
            body.append(line)
    if title:
        sections[title] = "\n".join(body).strip()
    return sections
