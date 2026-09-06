# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

This is a sample project used to demonstrate Claude Code and its features. The app itself
(a small FastAPI expense tracker) is secondary — the primary deliverable is `README.md`,
which is a living "Claude Code Best Practices" doc that grows as new features (permissions,
slash commands, hooks, marketplace, subagents, MCP, etc.) are explored in this repo. Keep
that ~90% best-practices / ~10% app-description balance when editing `README.md`.

## Commands

```powershell
uv sync                              # install dependencies from uv.lock
uv run uvicorn main:app --reload     # run the dev server (http://127.0.0.1:8000)
uv run python main.py                # alternative: run directly (no --reload)
uv run black .                       # format code (check-only: uv run black --check .)
```

There is no test suite or build step configured in this project.

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
```

## Routes

| Method | Path              | Auth required | Returns                              |
|--------|-------------------|----------------|----------------------------------------|
| GET    | `/`               | —              | Redirect to `/dashboard` or `/login`   |
| GET    | `/login`          | —              | Login page                             |
| POST   | `/login`          | —              | Authenticate, sets session             |
| GET    | `/register`       | —              | Register page (demo, static account)   |
| POST   | `/register`       | —              | No-op, re-points to static credentials |
| GET    | `/logout`         | —              | Clears session, redirects to `/login`  |
| GET    | `/dashboard`      | yes            | Dashboard UI                           |
| GET    | `/terms`          | —              | Terms and Conditions page              |
| GET    | `/privacy`        | —              | Privacy Policy page                    |
| POST   | `/expenses`       | yes            | Create an expense (JSON)               |
| GET    | `/expenses`       | yes            | List expenses (JSON, `?category=`)     |
| GET    | `/expenses/{id}`  | yes            | Get a single expense (JSON)            |
| PUT    | `/expenses/{id}`  | yes            | Update an expense (JSON)               |
| DELETE | `/expenses/{id}`  | yes            | Delete an expense (JSON)               |
| GET    | `/summary`        | yes            | `{total_spent, by_category}` (JSON)    |

`terms`/`privacy` are public but still receive `authenticated`/`username` context so the
shared header renders the logout link when the visitor happens to be logged in.

## Schema (SQLite via SQLModel ORM)

Single table, defined as the `Expense` SQLModel class in `main.py`:

| Column     | Type              | Notes                                  |
|------------|-------------------|------------------------------------------|
| `id`       | `int`, optional   | Primary key, autoincrement               |
| `title`    | `str`             | Required                                 |
| `amount`   | `float`           | Required                                 |
| `category` | `str`             | Required, free text (not a foreign key)  |
| `spent_on` | `date`            | Defaults to today if not provided        |
| `notes`    | `str`, optional   | Free text                                |

`ExpenseCreate` is a separate non-table SQLModel used as the request body for create/update
— keep this split (table model vs. input model) rather than reusing `Expense` directly for
request validation. All DB access goes through SQLModel's `Session`/`select()` (the ORM
layer) — don't drop down to raw SQL or a second DB library. The engine is a single
module-level `engine` in `main.py`; get a session with `with Session(engine) as session:`.

## Coding conventions

- Format with **black** (`uv run black .`) before committing — config is in
  `pyproject.toml` (`line-length = 100`).
- Use type hints on all function signatures (params + return types), matching the existing
  style in `main.py` (e.g. `Optional[str]`, `-> None`). New route handlers and helpers
  should follow the same convention.
- Use SQLModel as the ORM for any new persisted data — define a new `SQLModel(table=True)`
  class rather than hand-writing SQL, consistent with the `Expense` model.

## Architecture

Single-file FastAPI app (`main.py`) with server-rendered Jinja2 templates and vanilla
JS/CSS — no frontend build step, no JS framework.

- **Auth**: session-based via `starlette.middleware.sessions.SessionMiddleware`, backed by
  one hardcoded static account (`STATIC_USERNAME`/`STATIC_PASSWORD`). `is_authenticated()`
  and `require_auth()` gate page routes and the `/expenses*`/`/summary` API respectively.
  `/register` is a demo no-op that just points users back to the static credentials.
- **Data/routes**: see the Routes and Schema sections above. Page routes return
  `TemplateResponse`s; `/expenses*` and `/summary` return JSON, called from the dashboard's
  inline `<script>` via `fetch`. `/summary` computes total spend and a per-category
  breakdown by iterating all expenses in Python (no SQL aggregation).
- **Templates** (`templates/`): `_header.html` and `_footer.html` are shared partials
  included via Jinja `{% include %}` on every page for a consistent header/footer. Pages
  that include the header must set `class="has-header"` on `<body>` (see CSS notes below)
  and pass `authenticated`/`username` into the template context — the header shows the
  logout link and links the brand icon to `/dashboard` only when `authenticated` is true.
- **Styling** (`static/style.css`): one global stylesheet, no preprocessor. Two structural
  points to preserve when editing:
  - `.topbar` and `.site-footer` are `position: fixed` (top/bottom of viewport) on every
    page. `body` has `padding-bottom` for the fixed footer; `body.has-header` adds
    `padding-top` for the fixed header. Any new page reusing `_header.html` needs the
    `has-header` body class or content will render underneath the fixed bar.
  - The dashboard uses a sidebar + stat-cards + Chart.js layout (`.dash-layout`,
    `.sidebar`, `.stats-row`, `.dash-grid`) — the sidebar's `position: sticky` offset is
    `calc(var(--header-h) + 24px)` to clear the fixed header.
- **Charts**: Chart.js is loaded via CDN `<script>` tag directly in `dashboard.html` (no
  npm/bundler) and driven by a small inline script that renders a doughnut chart from
  `/summary`'s `by_category` data.
