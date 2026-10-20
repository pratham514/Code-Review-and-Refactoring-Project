"""Code-quality metrics for the legacy script and the refactored package.

Standard library only. Usage: python tools/measure_quality.py
"""
import ast
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGETS = {
    "BEFORE (legacy/sales_report.py)": [os.path.join(ROOT, "legacy", "sales_report.py")],
    "AFTER (salesreport/*.py)": sorted(glob.glob(os.path.join(ROOT, "salesreport", "*.py"))),
}
BRANCHES = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.BoolOp, ast.IfExp, ast.comprehension)
NESTING = (ast.If, ast.For, ast.While, ast.Try, ast.With)
WINDOW = 5   # consecutive lines compared when looking for duplicated code


def nesting_depth(node, depth=0):
    deepest = depth
    for child in ast.iter_child_nodes(node):
        step = 1 if isinstance(child, NESTING) else 0
        deepest = max(deepest, nesting_depth(child, depth + step))
    return deepest


def code_lines(source):
    """Non-blank lines that are not pure comments."""
    return [l.strip() for l in source.splitlines() if l.strip() and not l.strip().startswith("#")]


def duplicate_windows(all_lines):
    seen, dupes = {}, 0
    for i in range(len(all_lines) - WINDOW + 1):
        key = "\n".join(all_lines[i:i + WINDOW])
        if len(set(all_lines[i:i + WINDOW])) < 3:      # ignore trivial repeats such as "}" or "out ="
            continue
        seen[key] = seen.get(key, 0) + 1
    for count in seen.values():
        if count > 1:
            dupes += count - 1
    return dupes


def analyse(paths):
    totals = dict(loc=0, funcs=[], doc=0, doc_total=0, hinted=0, bare=0, magic=0,
                  glob=0, short=0, depth=0, lines=[])
    for path in paths:
        source = open(path, encoding="utf-8").read()
        tree = ast.parse(source)
        lines = code_lines(source)
        totals["loc"] += len(lines)
        totals["lines"].extend(lines)
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        totals["doc"] += sum(1 for n in funcs + classes if ast.get_docstring(n))
        totals["doc"] += 1 if ast.get_docstring(tree) else 0
        totals["doc_total"] += len(funcs) + len(classes) + 1
        totals["hinted"] += sum(1 for f in funcs if f.returns is not None)
        for f in funcs:
            length = f.end_lineno - f.lineno + 1
            complexity = 1 + sum(isinstance(c, BRANCHES) for c in ast.walk(f))
            totals["funcs"].append((f.name, length, complexity))
            totals["depth"] = max(totals["depth"], nesting_depth(f))
            names = {n.id for n in ast.walk(f) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
            totals["short"] += sum(1 for n in names if len(n) <= 2 and n != "_")
            for c in ast.walk(f):
                if isinstance(c, ast.Constant) and isinstance(c.value, (int, float)) \
                        and not isinstance(c.value, bool) and c.value not in (0, 1, 2):
                    totals["magic"] += 1
                if isinstance(c, ast.Global):
                    totals["glob"] += 1
                if isinstance(c, ast.ExceptHandler) and c.type is None:
                    totals["bare"] += 1
    return totals


def main():
    results = {name: analyse(paths) for name, paths in TARGETS.items()}
    rows = []
    for t in results.values():
        lengths = [f[1] for f in t["funcs"]]
        cx = [f[2] for f in t["funcs"]]
        rows.append({
            "Code lines (no blanks/comments)": t["loc"],
            "Functions/methods": len(t["funcs"]),
            "Longest function (lines)": max(lengths),
            "Average function length (lines)": f"{sum(lengths) / len(lengths):.1f}",
            "Highest cyclomatic complexity": max(cx),
            "Average cyclomatic complexity": f"{sum(cx) / len(cx):.1f}",
            "Deepest nesting (levels)": t["depth"],
            "Duplicated 5-line blocks": duplicate_windows(t["lines"]),
            "'global' statements": t["glob"],
            "Bare 'except:' handlers": t["bare"],
            "Magic numbers inside functions": t["magic"],
            "Variables with 1-2 letter names": t["short"],
            "Docstring coverage": f"{100 * t['doc'] // t['doc_total']}%",
            "Functions with return type hints": f"{100 * t['hinted'] // len(t['funcs'])}%",
        })
    names = list(results)
    print(f"{'Metric':<36}{'BEFORE (legacy)':<20}{'AFTER (package)'}")
    for metric in rows[0]:
        print(f"{metric:<36}{str(rows[0][metric]):<20}{rows[1][metric]}")
    print()
    print("Longest functions before:", sorted(results[names[0]]["funcs"], key=lambda f: -f[1])[:3])
    print("Longest functions after: ", sorted(results[names[1]]["funcs"], key=lambda f: -f[1])[:3])


if __name__ == "__main__":
    main()
