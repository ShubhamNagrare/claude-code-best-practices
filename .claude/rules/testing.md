# Testing

## Current state: no automated tests exist

There is no test suite, test runner, or test dependency configured anywhere in this
project (no `tests/` directory, no `pytest`/`unittest` in `pyproject.toml`). Don't assume
tests exist or reference a "test command" that isn't real — `uv run black .` is currently
the only automated check in this repo (formatting, not correctness).

All verification of behavior so far has been **manual, via a running server**:

- `uv run uvicorn main:app --reload`, then either `curl`/browser for a quick check, or
  driving Chrome via `claude-in-chrome` (navigate, screenshot, fill forms, and — important —
  cross-check with `read_network_requests`/`javascript_tool` rather than trusting a
  screenshot alone, since automated clicks can silently miss).
- This is a reasonable interim approach for a small demo app, but it's not a substitute for
  a real test suite the moment this project grows business logic worth protecting.

## If/when adding automated tests

This is a FastAPI + SQLModel app, so the natural choice (don't reach for anything else
without a reason):

- **Runner**: `pytest`, added as a dev dependency the same way `black` was:
  `uv add --dev pytest`. Run with `uv run pytest`.
- **HTTP client**: FastAPI's `fastapi.testclient.TestClient` (wraps `httpx`) for calling
  routes in-process — no need to actually run `uvicorn` for tests.
- **Test database**: never point tests at `database/spend_tracker.db` (the real dev data).
  Use a separate SQLite file (e.g. `sqlite:///./database/test.db`, deleted between runs) or
  an in-memory engine (`sqlite:///:memory:` with `StaticPool`), constructed the same way
  `main.py` builds its engine, and override `main.engine`/the session dependency for the
  test client rather than mutating the module-level `engine` in place.
- **Layout**: given the app is a single `main.py`, mirror it with a small number of test
  modules grouped by concern rather than one-test-per-route-file, e.g.:
  ```
  tests/
    test_auth.py       # /login, /register, /logout, session behavior
    test_expenses.py   # /expenses CRUD + /summary
    test_pages.py       # page routes render / redirect correctly when (un)authenticated
  ```
- **Auth in tests**: register a test user via `POST /register`, then log in through
  `POST /login` with those credentials to obtain a session cookie via `TestClient`, then
  reuse that client for authenticated requests — don't hand-construct session cookies
  manually.
- **What to cover first** (highest value given current code):
  - Auth gating: protected routes reject unauthenticated requests (`401`/redirect) and
    accept authenticated ones.
  - `/expenses` CRUD round-trip (create → get → update → delete → 404 after delete).
  - `/summary` totals and per-category breakdown match the created expenses.
  - `PUT /expenses/{id}` partial-update behavior (only sent fields change) — this is a
    real nuance in the current code (see `api-convention.md`) worth locking in with a test.
  - Registration uniqueness: duplicate username, duplicate email, and both-duplicate cases
    each produce the correct distinct message and do not create a row.
  - Per-user expense scoping: a second user cannot see, update, or delete a first user's
    expenses (expect `404`, not `403`, per the non-disclosure convention).

## What not to do

- Don't share one hardcoded test user across test modules if tests might run in parallel or
  against a shared DB — register a fresh user (unique username/email) per test/module to
  avoid uniqueness collisions.
- Don't add a test dependency (pytest plugins, faker, factory libraries, etc.) without
  updating `pyproject.toml` and noting it in `CLAUDE.md`, same rule as for any other tool.
- Don't write tests that depend on wall-clock date/time without freezing or injecting it —
  `spent_on` defaults to `date.today()`.
