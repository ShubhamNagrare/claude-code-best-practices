# Code Style

Coding conventions observed in this project. Follow these when adding or editing code so
the codebase stays consistent — don't introduce a new style even if it's "more correct" in
isolation.

## Python (`main.py`)

- **Formatter**: black, line-length 100 (`uv run black .`). Run it before committing —
  don't hand-format to "look like black", just run it.
- **Type hints everywhere**: every function signature has parameter and return types,
  including `-> None` for functions with no return value. Use `Optional[X]` (not `X | None`)
  to match the existing style.
  ```python
  def is_authenticated(request: Request) -> bool:
      return bool(request.session.get("user"))

  def require_auth(request: Request) -> None:
      if not is_authenticated(request):
          raise HTTPException(status_code=401, detail="Not authenticated")
  ```
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
  (`Expense`, `ExpenseCreate`), `UPPER_SNAKE_CASE` for module-level constants
  (`DATABASE_URL`, `SESSION_SECRET_KEY`).
- **ORM, not raw SQL**: persisted data is modeled as a `SQLModel(table=True)` class;
  query with `select()` / `session.get()`, not hand-written SQL strings. Use a separate
  non-table `SQLModel` (e.g. `ExpenseCreate`) as the request/input schema rather than
  reusing the table model for validation — keeps the DB shape and the API input shape
  independent.
- **Sessions**: open a DB session per request with a context manager, don't hold one open
  across requests:
  ```python
  with Session(engine) as session:
      ...
  ```
- **Auth checks**: call `require_auth(request)` explicitly as the first line of a
  protected handler (not a FastAPI `Depends`). Page routes that gate on auth instead
  check `is_authenticated(request)` and return a `RedirectResponse`.
- **No docstrings, no inline comments**: names should carry the meaning. Only comment
  something non-obvious (a workaround, a subtle constraint) — there are currently zero
  comments in `main.py` and that's intentional, not an oversight.
- **Imports**: standard library first, then third-party, each group in the order used —
  don't reorder existing imports for alphabetization alone.
- **Route handlers**: name the function after what it does, not the HTTP verb + path
  (`login_page` vs `login_submit`, `terms_page`, `dashboard`). JSON API handlers declare
  `response_model=` on the decorator when returning a model instance.

## Templates (`templates/*.html`, Jinja2)

- **2-space indentation**, not 4.
- **Shared chrome lives in partials**: cross-page markup (header, footer) goes in a
  leading-underscore partial (`_header.html`, `_footer.html`) and is pulled in with
  `{% include "_partial.html" %}` — never copy-paste header/footer markup into a new page.
- Pages that include `_header.html` must set `class="has-header"` on `<body>` and pass
  `authenticated` / `username` into the template context (see CSS note below on why).
- Page-specific behavior is a single inline `<script>` at the end of `<body>`, after any
  CDN `<script src>` tags it depends on (e.g. Chart.js before the dashboard's chart code).
  No bundler, no separate `.js` files — keep it that way unless a page's script grows large
  enough to genuinely need one.

## CSS (`static/style.css`)

- **Single global stylesheet**, no preprocessor, no utility framework (no Tailwind/Bootstrap).
- **kebab-case class names** (`dash-layout`, `stat-card`, `category-row`), not BEM, not
  camelCase.
- Section the file with a plain comment header above each logical block, matching the
  existing style: `/* Dashboard */`, `/* Footer */`, `/* Legal pages */`.
- Shared sizing that multiple rules depend on is a CSS custom property on `:root`
  (`--header-h`, `--footer-h`) rather than a repeated magic number.
- Responsive breakpoints are a `@media (max-width: ...)` block placed immediately after
  the rules it overrides, not collected in one file-wide media query.

## JavaScript (inline, vanilla)

- **No framework, no build step, no TypeScript.** Plain ES6+ in a `<script>` tag.
- `const`/`let` only — never `var`.
- `camelCase` for variables and functions; DOM lookups are named `<thing>El`
  (`rowsEl`, `categoriesEl`, `statTotalEl`).
- Cache `document.getElementById(...)` results in a top-level `const` once, don't re-query
  the same element repeatedly.
- Async I/O uses `async`/`await` with `fetch`, not `.then()` chains.
- Build HTML fragments with template literals + `innerHTML` for list rendering (see
  `loadExpenses()` in `dashboard.html`) — consistent with the rest of the file; this is a
  small demo app so this is fine, don't introduce a templating library for it.
- A `401` response from any API call redirects to `/login` client-side
  (`if (res.status === 401) { window.location.href = '/login'; ... }`) — repeat this check
  on any new fetch call against a protected endpoint.

## General

- Don't add a linter/formatter/tool beyond what's already configured (black for Python)
  without updating `pyproject.toml` and documenting it in `CLAUDE.md`.
- Keep the "no comments unless the WHY is non-obvious" rule across all languages here, not
  just Python — the templates and CSS also currently have none beyond CSS section headers.
