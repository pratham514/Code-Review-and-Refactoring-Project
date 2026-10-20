# Week 4: Code Review and Refactoring Project

A peer-style code review and refactoring of a small sales-report program. The project contains the **original ("legacy") script**, a written **code review** (20 findings), the **refactored package**, 48 automated tests that prove the behaviour is preserved, and tools that measure the improvement.

The full review report is in `docs/Code_Review_Report.docx` (it also contains the complete refactored code).

## What the program does

It reads an orders CSV file and prints four reports: a summary, revenue by category, the top 3 customers, and monthly revenue. Discounts: 10% for 10+ items, 15% for 50+ items, +5% for VIP customers, +2% for electronics, capped at 20%.

## Results at a glance

| Measure | Before | After |
|---|---|---|
| Average cyclomatic complexity per function | 10.6 | 1.7 |
| Longest function (lines) | 45 | 24 |
| Duplicated 5-line blocks | 26 | 0 |
| Global variables / bare `except:` | 1 `global` statement / 1 | 0 / 0 |
| Magic numbers inside functions | 50 | 0 |
| Docstring coverage | 0% | 100% |
| Return type hints | 0% | 100% |
| Automated tests | 0 | 48 |
| Run time, 20,000 orders | 1.07 s | 0.17 s (6.3x faster) |

## Project structure

```
week4-code-review-refactoring/
├── legacy/sales_report.py      # original script, unchanged ("before")
├── salesreport/                # refactored package ("after")
│   ├── models.py               # data classes
│   ├── pricing.py              # discount rules (single implementation)
│   ├── loader.py               # CSV reading and validation
│   ├── reports.py              # calculations (pure functions)
│   ├── formatting.py           # text output
│   ├── cli.py                  # command-line interface
│   └── __main__.py             # python -m salesreport
├── tests/                      # 48 unit and regression tests
├── tools/                      # measurement and demo scripts
├── data/sample_orders.csv      # sample input
├── docs/                       # review report, real outputs, diagrams
└── README.md
```

## Requirements

Python 3.8 or newer. No third-party packages.

## Installation

```bash
git clone https://github.com/pratham514/week4-code-review-refactoring.git
cd week4-code-review-refactoring
```

## Usage

Run the refactored program:

```bash
python -m salesreport data/sample_orders.csv
```

Run the original program for comparison:

```bash
python legacy/sales_report.py data/sample_orders.csv
```

Run all tests (including the tests that compare the old and new programs):

```bash
python -m unittest discover -s tests -v
```

Measure the improvement:

```bash
python tools/measure_quality.py      # complexity, duplication, docs, naming
python tools/coverage_report.py      # line coverage
python tools/benchmark.py            # run time before vs after
python tools/profile_legacy.py       # where the legacy script spends its time
python tools/demo_legacy_defects.py  # two defects found during the review
```

## Intentional behaviour changes

The refactoring keeps the output identical for valid data, with three deliberate exceptions found during the review:

| ID | Change | Reason |
|----|--------|--------|
| R03 | "Top customers" now includes the VIP discount | The legacy copy of the discount code forgot it, so this report disagreed with the others (Alice: 9293.58 before, 8885.58 after) |
| R15 | A missing file prints a friendly error and exits with code 2 | The legacy script crashed with a traceback |
| R19 | Dates like `2026-3-5` are grouped under `2026-03` | The legacy script produced the month label `2026-3-` |

## Author

Pratham
