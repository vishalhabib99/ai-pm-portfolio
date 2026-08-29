"""
ACRS demo API - thin FastAPI wrapper around the reviewed score_v2 scorer at
../prototypes/agent-codebase-readiness-score/score_v2.py. This does not
duplicate that logic: it imports it directly, so the live demo and the
disclosed-limitations write-up next to it can never drift apart.

Safety, since this clones arbitrary user-submitted GitHub URLs:
- github.com URLs only, validated by a strict regex (no shell=True anywhere,
  all subprocess calls use argument lists)
- shallow clone (depth matches the churn window), size-capped after clone
- one scoring job at a time (in-process lock) plus a per-IP rate limit
- only ever reads/parses cloned files (git log, ast.parse) - never executes
  anything from the target repo
"""

import asyncio
import os
import re
import subprocess
import sys
import tempfile
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__), "..", "prototypes", "agent-codebase-readiness-score"
    ),
)
from score_v2 import score_repo_v2  # noqa: E402

GITHUB_URL_RE = re.compile(
    r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?/?$"
)
CLONE_DEPTH = 300
CLONE_TIMEOUT_S = 45
MAX_REPO_MB = 200

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="ACRS demo")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

scoring_lock = asyncio.Lock()


class ScoreRequest(BaseModel):
    repo_url: str
    package_name: Optional[str] = None


def _dir_size_mb(path: str) -> float:
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total / (1024 * 1024)


def _run_clone_and_score(repo_url: str, package_name: str):
    with tempfile.TemporaryDirectory(prefix="acrs_") as tmp:
        try:
            subprocess.run(
                ["git", "clone", "--depth", str(CLONE_DEPTH), "--single-branch", repo_url, tmp],
                check=True,
                capture_output=True,
                text=True,
                timeout=CLONE_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(504, "Clone timed out - repo may be too large for this demo.")
        except subprocess.CalledProcessError as e:
            raise HTTPException(400, f"Could not clone that repo: {e.stderr.strip()[:300]}")

        size_mb = _dir_size_mb(tmp)
        if size_mb > MAX_REPO_MB:
            raise HTTPException(
                413, f"Repo is ~{size_mb:.0f}MB, over this demo's {MAX_REPO_MB}MB cap."
            )

        src_layout_found = os.path.isdir(os.path.join(tmp, "src", package_name))
        try:
            results, symbol_map = score_repo_v2(tmp, package_name)
        except Exception as e:
            raise HTTPException(400, f"Scoring failed: {e}")

        return {
            "results": results,
            "resolved_symbols": len(symbol_map),
            "src_layout_found": src_layout_found,
            "warning": None
            if src_layout_found
            else (
                "No src/<package_name>/ layout found - scored top-level repo "
                "directories instead, which may include non-source folders "
                "(docs, tests, etc.) as separate 'modules'. Try setting "
                "package_name explicitly if this looks wrong."
            ),
        }


@app.post("/api/score")
@limiter.limit("5/hour")
async def score(request: Request, body: ScoreRequest):
    match = GITHUB_URL_RE.match(body.repo_url.strip())
    if not match:
        raise HTTPException(400, "Enter a plain https://github.com/owner/repo URL.")
    owner, repo = match.group(1), match.group(2)
    package_name = (body.package_name or repo).replace("-", "_")

    if scoring_lock.locked():
        raise HTTPException(
            429, "Demo is scoring another repo right now - try again in a moment."
        )

    async with scoring_lock:
        clone_url = f"https://github.com/{owner}/{repo}.git"
        return await asyncio.to_thread(_run_clone_and_score, clone_url, package_name)


app.mount(
    "/",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static"), html=True),
    name="static",
)
