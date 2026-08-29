# ACRS live demo

**Try it: https://acrs-demo.onrender.com** (free tier - sleeps after 15min
idle, first request can take ~30s to wake it up)

A thin FastAPI wrapper around the reviewed scorer at
[`prototypes/agent-codebase-readiness-score/score_v2.py`](../prototypes/agent-codebase-readiness-score/).
It imports that file directly rather than copying it, so this demo and the
case study's disclosed limitations can't drift apart.

Paste a public GitHub repo URL, get back the same per-module readiness table
described in the case study - live, on whatever repo you give it.

## Run locally

```
cd demo
pip install -r requirements.txt
uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000`.

## Safety limits (this clones arbitrary user-submitted URLs)

- `github.com` URLs only, validated by a strict regex - no shell execution,
  every subprocess call uses an argument list
- shallow clone (depth 300, matching the churn window)
- repo size capped at 200MB after clone
- 45s clone timeout
- one scoring job at a time (in-process lock), 5 requests/hour per IP
- only ever reads and statically analyzes the cloned repo (`git log`,
  `ast.parse`) - never executes anything from it

## Known limitation carried over from the prototype

The scorer expects a `src/<package_name>/` layout (or falls back to treating
every top-level directory as a "module", which can include non-source
folders like `docs/` or `tests/`). The demo surfaces this as an explicit
warning in the UI rather than silently returning misleading numbers - same
honesty standard as the rest of this portfolio.

## Deploy (Render)

This repo includes a `render.yaml` at the root as a reference for the
service config (root dir `demo/`, free plan, `uvicorn app:app` on `$PORT`,
`PYTHON_VERSION` pinned to 3.11.9 to avoid pulling an unreleased-wheel
version of `pydantic-core`). The live instance was created via the Render
CLI (`render services create`) against a GitHub App-connected repo, so
pushes to `main` auto-deploy.
