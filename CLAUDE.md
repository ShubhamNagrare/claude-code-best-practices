# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is a sample project used to demonstrate Claude Code and its features. The app itself
(a small FastAPI expense tracker) is secondary — the primary deliverable is `README.md`,
which is a living "Claude Code Best Practices" doc that grows as new features (permissions,
slash commands, hooks, marketplace, subagents, MCP, etc.) are explored in this repo. Keep
that ~90% best-practices / ~10% app-description balance when editing `README.md`.

## Rules

Detailed, topic-specific conventions live in `.claude/rules/` and are imported below so
they load every session — read the relevant one before touching that part of the codebase:

@.claude/rules/code-style.md
@.claude/rules/api-convention.md
@.claude/rules/security.md
@.claude/rules/testing.md
@.claude/rules/git-workflow.md

## Commands

```powershell
uv sync                              # install dependencies from uv.lock
uv run uvicorn main:app --reload     # run the dev server (http://127.0.0.1:8000)
uv run python main.py                # alternative: run directly (no --reload)
uv run black .                       # format code (check-only: uv run black --check .)
```

Demo login: username `username` / password `password` (hardcoded in `main.py`).

## Project directory

```
main.py              # entire app: models, routes, auth — single-file FastAPI
pyproject.toml        # deps (uv) + black config
uv.lock                # locked dependency versions
database/
  spend_tracker.db    # SQLite file, created on startup, gitignored
templates/
  _header.html         # shared header partial (topbar, logout)
  _footer.html         # shared footer partial (Terms/Privacy links)
  login.html
  register.html
  dashboard.html
  terms.html
  privacy.html
static/
  style.css            # single global stylesheet, no preprocessor
.claude/rules/          # topic-specific conventions, imported above
```

## Architecture

Single-file FastAPI app (`main.py`) with server-rendered Jinja2 templates and vanilla
JS/CSS — no frontend build step, no JS framework.

- **Auth**: session-based via `starlette.middleware.sessions.SessionMiddleware` against one
  hardcoded static account. `is_authenticated()`/`require_auth()` gate page routes and the
  `/expenses*`/`/summary` API respectively — see `security.md` for the full threat-model
  notes and `api-convention.md` for the endpoint table.
- **Data model**: a single `Expense` SQLModel table (`id`, `title`, `amount`, `category`,
  `spent_on`, `notes`) backed by SQLite at `database/spend_tracker.db` — path is built from
  `Path(__file__).parent / "database"` (not cwd-relative), folder auto-created on import.
  `*.db` is gitignored. See `code-style.md` for the ORM/session conventions and
  `api-convention.md` for the input-model-vs-table-model split.
- **Templates**: `_header.html`/`_footer.html` are shared partials (see `code-style.md`).
  The one thing not to forget: `.topbar` and `.site-footer` are `position: fixed` on every
  page, so `body` needs `padding-bottom` (global) and `body.has-header` needs `padding-top`
  — any new page including `_header.html` must add the `has-header` class or its content
  renders underneath the fixed bar. The dashboard's sidebar is `position: sticky` with a
  `calc(var(--header-h) + 24px)` offset to clear that same fixed header.
- **Charts**: Chart.js loaded via CDN `<script>` tag in `dashboard.html` (no bundler),
  driven by a small inline script rendering a doughnut chart from `/summary`.
