"""Line coverage of the salesreport package using only the standard library.

Usage: python tools/coverage_report.py
(With the third-party tool:  coverage run -m unittest discover -s tests; coverage report -m)
"""
import glob
import os
import sys
import trace
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = sorted(glob.glob(os.path.join(ROOT, "salesreport", "*.py")))


def run_all():
    sys.path.insert(0, ROOT)
    suite = unittest.defaultTestLoader.discover(os.path.join(ROOT, "tests"))
    return unittest.TextTestRunner(stream=open(os.devnull, "w")).run(suite)


def main():
    tracer = trace.Trace(count=1, trace=0)
    result = tracer.runfunc(run_all)
    counts = tracer.results().counts
    print(f"Tests run: {result.testsRun}, failures/errors: {len(result.failures) + len(result.errors)}")
    print("(tests that start the program in a separate process do not add to these numbers)")
    print(f"{'File':<28}{'Lines':>7}{'Covered':>9}{'Coverage':>10}")
    total_exec = total_hit = 0
    for path in FILES:
        executable = set(trace._find_executable_linenos(path)) - {0}
        hit = {line for (p, line), _ in counts.items() if os.path.abspath(p) == path}
        covered = executable & hit
        total_exec += len(executable)
        total_hit += len(covered)
        name = os.path.relpath(path, ROOT).replace(os.sep, "/")
        print(f"{name:<28}{len(executable):>7}{len(covered):>9}{100 * len(covered) / max(len(executable), 1):>9.0f}%")
    print(f"{'TOTAL':<28}{total_exec:>7}{total_hit:>9}{100 * total_hit / total_exec:>9.0f}%")


if __name__ == "__main__":
    main()
