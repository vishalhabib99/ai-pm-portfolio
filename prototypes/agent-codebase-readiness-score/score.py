"""
Agent Codebase Readiness Score (ACRS) — prototype scorer.

Computes a per-module readiness score for a real target codebase using
static-analysis + git-history proxies, matching the PRD's "per-module
scoring, not one number" approach:
https://github.com/vishalhabib99/ai-pm-portfolio/blob/main/prds/2026-08-agent-codebase-readiness-score.md

IMPORTANT SCOPE NOTE (read this before trusting the numbers):
This prototype uses cheap, computable PROXIES for the PRD's real scoring
dimensions — it does NOT run actual coding agents against sampled tasks.
  - "context understanding" dimension -> proxied by docstring density + avg file size
  - "task success rate" dimension     -> proxied by module churn + test-reference density
A real v1 (per the PRD) would sample actual historical PRs and measure real
agent success/cost/quality on them. This prototype exists to prove the
per-module scoring structure and produce a real, inspectable output on a
real codebase — not to make a validated readiness claim.

Run: python3 score.py <path-to-target-repo>
"""

import ast
import os
import subprocess
import sys

def find_modules(src_root):
    """Top-level subdirectories of src_root are modules; loose .py files
    directly in src_root are grouped into a 'core' module."""
    modules = {}
    core_files = []
    for entry in sorted(os.listdir(src_root)):
        full = os.path.join(src_root, entry)
        if os.path.isdir(full) and not entry.startswith("__") and not entry.startswith("."):
            py_files = []
            for dirpath, _, filenames in os.walk(full):
                for fn in filenames:
                    if fn.endswith(".py"):
                        py_files.append(os.path.join(dirpath, fn))
            if py_files:
                modules[entry] = py_files
        elif entry.endswith(".py"):
            core_files.append(full)
    if core_files:
        modules["core"] = core_files
    return modules


def docstring_density(py_files):
    """Fraction of function/class defs that have a docstring."""
    total_defs = 0
    documented = 0
    for path in py_files:
        try:
            with open(path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=path)
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                total_defs += 1
                if ast.get_docstring(node):
                    documented += 1
    return documented / total_defs if total_defs else 0.0


def avg_file_lines(py_files):
    total_lines = 0
    for path in py_files:
        try:
            with open(path, encoding="utf-8") as f:
                total_lines += sum(1 for _ in f)
        except UnicodeDecodeError:
            continue
    return total_lines / len(py_files) if py_files else 0.0


def churn_count(repo_root, py_files, n_commits=300):
    """Number of commits (within the cloned history window) touching this module's files."""
    rel_files = [os.path.relpath(p, repo_root) for p in py_files]
    if not rel_files:
        return 0
    result = subprocess.run(
        ["git", "log", f"-{n_commits}", "--oneline", "--", *rel_files],
        cwd=repo_root, capture_output=True, text=True,
    )
    return len([line for line in result.stdout.splitlines() if line.strip()])


def test_reference_count(repo_root, module_name):
    """How many test files reference this module by name — proxy for test coverage."""
    tests_dir = os.path.join(repo_root, "tests")
    if not os.path.isdir(tests_dir):
        return 0
    result = subprocess.run(
        ["grep", "-rl", module_name, tests_dir],
        capture_output=True, text=True,
    )
    return len([line for line in result.stdout.splitlines() if line.strip()])


def normalize(value, lo, hi):
    if hi == lo:
        return 0.5
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def score_repo(repo_root):
    src_root = os.path.join(repo_root, "src", "flask")
    if not os.path.isdir(src_root):
        # fall back to repo root if no src/<pkg> layout
        src_root = repo_root

    modules = find_modules(src_root)
    raw = {}
    for name, files in modules.items():
        raw[name] = {
            "doc_density": docstring_density(files),
            "avg_lines": avg_file_lines(files),
            "churn": churn_count(repo_root, files),
            "test_refs": test_reference_count(repo_root, name),
            "n_files": len(files),
        }

    all_avg_lines = [m["avg_lines"] for m in raw.values()]
    all_churn = [m["churn"] for m in raw.values()]
    all_test_refs = [m["test_refs"] for m in raw.values()]

    results = []
    for name, m in raw.items():
        doc_score = m["doc_density"]  # already 0-1, higher = better
        size_score = 1 - normalize(m["avg_lines"], min(all_avg_lines), max(all_avg_lines))  # smaller files = better
        stability_score = 1 - normalize(m["churn"], min(all_churn), max(all_churn))  # less churn = better
        test_score = normalize(m["test_refs"], min(all_test_refs), max(all_test_refs))  # more test refs = better

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
    return results


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "target_repo"
    results = score_repo(target)

    print(f"{'module':12} {'readiness':10} {'doc_dens':9} {'avg_lines':10} {'churn':7} {'test_refs':10} {'files'}")
    for r in results:
        print(f"{r['module']:12} {r['readiness']:<10} {r['doc_density']:<9} {r['avg_lines']:<10} "
              f"{r['churn_commits']:<7} {r['test_refs']:<10} {r['n_files']}")

    print()
    print("Highest readiness (safest for early/autonomous agent use):", results[0]["module"])
    print("Lowest readiness (keep human-in-the-loop):", results[-1]["module"])
