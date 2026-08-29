"""
ACRS scorer, v2 — fixes the test_refs bug found and disclosed in v1's README
(https://github.com/vishalhabib99/ai-pm-portfolio/blob/main/prototypes/agent-codebase-readiness-score/README.md).

v1 bug: grepped test files for the literal module directory name as a
string, which fails whenever a codebase re-exports symbols through a
package __init__.py (e.g. `from flask import Flask`, not
`from flask.app import Flask`) — extremely common, and it silently zeroed
out test_refs for 2 of Flask's 3 modules.

v2 fix: build an actual symbol -> submodule map by parsing the package's
__init__.py re-exports with ast, then resolve each test file's imports
(and `pkg.symbol` attribute usage) against that map, instead of string
matching on the module's own name.

Run: python3 score_v2.py <path-to-target-repo> <package-name>
Example: python3 score_v2.py target_repo flask
"""

import ast
import os
import re
import sys

from score import find_modules, docstring_density, avg_file_lines, churn_count, normalize


def build_reexport_map(src_root, package_name):
    """Parse src_root/__init__.py; return {exported_symbol_name: submodule_name}."""
    init_path = os.path.join(src_root, "__init__.py")
    symbol_to_submodule = {}
    if not os.path.isfile(init_path):
        return symbol_to_submodule

    with open(init_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=init_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.level == 1:
            # "from . import json as json"  -> node.module is None, importing a submodule itself
            # "from .app import Flask as Flask" -> node.module == "app"
            for alias in node.names:
                exported_name = alias.asname or alias.name
                submodule = node.module if node.module else alias.name
                # only keep the first path segment (submodule or subpackage name)
                submodule = submodule.split(".")[0]
                symbol_to_submodule[exported_name] = submodule
    return symbol_to_submodule


def submodule_to_grouped_module(submodule_name, src_root):
    """Map a raw submodule name (e.g. 'app', 'json') to the module grouping
    find_modules() uses: subdirectories keep their name, loose .py files -> 'core'."""
    if os.path.isdir(os.path.join(src_root, submodule_name)):
        return submodule_name
    if os.path.isfile(os.path.join(src_root, submodule_name + ".py")):
        return "core"
    return None


def test_reference_count_v2(repo_root, package_name, src_root, module_group_name, symbol_to_submodule):
    """Count test files that reference this module group, via AST-resolved
    imports and `pkg.symbol` attribute access — not literal module-name grep."""
    tests_dir = os.path.join(repo_root, "tests")
    if not os.path.isdir(tests_dir):
        return 0

    matching_files = 0
    for dirpath, _, filenames in os.walk(tests_dir):
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fn)
            try:
                with open(fpath, encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=fpath)
            except (SyntaxError, UnicodeDecodeError):
                continue

            referenced_modules = set()

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module == package_name:
                        # from flask import Flask, jsonify, ...
                        for alias in node.names:
                            sub = symbol_to_submodule.get(alias.name)
                            if sub:
                                grouped = submodule_to_grouped_module(sub, src_root)
                                if grouped:
                                    referenced_modules.add(grouped)
                    elif node.module.startswith(package_name + "."):
                        # from flask.sansio import X
                        sub = node.module[len(package_name) + 1:].split(".")[0]
                        grouped = submodule_to_grouped_module(sub, src_root)
                        if grouped:
                            referenced_modules.add(grouped)

            # also catch `flask.Symbol` attribute usage after a bare `import flask`
            for match in re.finditer(rf"\b{re.escape(package_name)}\.(\w+)", source):
                sub = symbol_to_submodule.get(match.group(1))
                if sub:
                    grouped = submodule_to_grouped_module(sub, src_root)
                    if grouped:
                        referenced_modules.add(grouped)

            if module_group_name in referenced_modules:
                matching_files += 1

    return matching_files


def score_repo_v2(repo_root, package_name):
    src_root = os.path.join(repo_root, "src", package_name)
    if not os.path.isdir(src_root):
        src_root = repo_root

    modules = find_modules(src_root)
    symbol_map = build_reexport_map(src_root, package_name)

    raw = {}
    for name, files in modules.items():
        raw[name] = {
            "doc_density": docstring_density(files),
            "avg_lines": avg_file_lines(files),
            "churn": churn_count(repo_root, files),
            "test_refs": test_reference_count_v2(repo_root, package_name, src_root, name, symbol_map),
            "n_files": len(files),
        }

    all_avg_lines = [m["avg_lines"] for m in raw.values()]
    all_churn = [m["churn"] for m in raw.values()]
    all_test_refs = [m["test_refs"] for m in raw.values()]

    results = []
    for name, m in raw.items():
        doc_score = m["doc_density"]
        size_score = 1 - normalize(m["avg_lines"], min(all_avg_lines), max(all_avg_lines))
        stability_score = 1 - normalize(m["churn"], min(all_churn), max(all_churn))
        test_score = normalize(m["test_refs"], min(all_test_refs), max(all_test_refs))

        readiness = 100 * (0.30 * doc_score + 0.20 * size_score + 0.20 * stability_score + 0.30 * test_score)
        results.append({
            "module": name,
            "readiness": round(readiness, 1),
            "doc_density": round(m["doc_density"], 2),
            "avg_lines": round(m["avg_lines"], 0),
            "churn_commits": m["churn"],
            "test_refs": m["test_refs"],
            "n_files": m["n_files"],
        })

    results.sort(key=lambda r: -r["readiness"])
    return results, symbol_map


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "target_repo"
    package = sys.argv[2] if len(sys.argv) > 2 else "flask"

    results, symbol_map = score_repo_v2(target, package)

    print(f"Resolved {len(symbol_map)} re-exported symbols from {package}/__init__.py")
    print()
    print(f"{'module':12} {'readiness':10} {'doc_dens':9} {'avg_lines':10} {'churn':7} {'test_refs':10} {'files'}")
    for r in results:
        print(f"{r['module']:12} {r['readiness']:<10} {r['doc_density']:<9} {r['avg_lines']:<10} "
              f"{r['churn_commits']:<7} {r['test_refs']:<10} {r['n_files']}")
