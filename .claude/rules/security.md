# Security

This is a demo app, not a production system — several things below are *intentionally*
simplified for the demo and are flagged as such. Don't "fix" them without being asked, but
also don't copy the demo shortcuts into anything meant to go further than this repo.

## Auth model (current state)

- Session auth via `starlette.middleware.sessions.SessionMiddleware` — a signed (not
  encrypted) cookie holding `{"user": "<username>"}`. Signing key is `SESSION_SECRET_KEY`,
  hardcoded in `main.py`. **Demo-only**: a real deployment must load this from an
  environment variable / secret manager, never commit it, and rotate it per environment.
- Login authenticates against the `users` table by username, with `passlib`/`bcrypt`
  password hashing (`hash_password`/`verify_password` in `main.py`) — plaintext passwords
  are never stored or compared. There is no shared static account anymore.
- `/register` creates a real `User` row after checking username and email uniqueness
  against the database independently, returning a specific message for whichever field
  collided (see `api-convention.md`). This is a real registration flow, not a demo no-op.
- No rate limiting or lockout on `/login` — brute-forcing a user's password is not
  mitigated. Not a concern for the demo; would be for anything real.

## Authorization pattern

- Every protected page route checks `is_authenticated(request)` and redirects to
  `/login` if false. Every protected JSON API route calls `require_auth(request)` (raises
  `401`) as its first line. **New protected routes must follow this same explicit-check
  pattern** — don't introduce a different auth mechanism (e.g. FastAPI `Depends`) for only
  part of the app.
- `/terms` and `/privacy` are intentionally public (no auth check) — they still read
  session state to decide whether to show the logout link, but never require it.

## Known gap: unescaped user content in the dashboard

`dashboard.html`'s inline script inserts expense fields (`title`, `category`, `spent_on`)
directly into `innerHTML` via template literals with no escaping:

```js
tr.innerHTML = `<td>${e.title}</td><td>${e.category}</td>...`;
```

Since `title`/`category`/`notes` are free-text fields a logged-in user controls, this is a
**stored-XSS-shaped pattern** (low real-world risk today since expenses are scoped to the
account that created them — a user could only attack themselves — but the pattern is wrong
regardless). If you touch this
code: escape values before inserting into `innerHTML`, or build nodes with
`textContent`/`createElement` instead of string concatenation. Don't extend this pattern
to new fields without addressing it.

## Cookies / transport

- `SessionMiddleware`'s cookie is `httponly` by default (good) but not marked `secure` —
  fine for local `http://127.0.0.1` dev, but a real deployment behind HTTPS should
  construct it with `https_only=True`.
- No CSRF protection on state-changing requests (`POST /login`, `POST/PUT/DELETE
  /expenses/*`). Acceptable for a same-origin demo with a single fetch-based frontend; a
  real multi-origin or third-party-embeddable version would need CSRF tokens or
  `SameSite`-cookie-based mitigation reviewed explicitly.
- No CORS middleware is configured — the app assumes the frontend and API are same-origin.
  Adding a separate frontend origin later means adding `CORSMiddleware` deliberately, not
  defaulting to `allow_origins=["*"]`.

## Data handling

- Expense data (`title`, `amount`, `category`, `spent_on`, `notes`, plus a `user_id` owner
  link) and account data (`username`, `email`, `password_hash`) are stored in
  `database/spend_tracker.db`, matching what `templates/privacy.html` discloses. If the
  fields the app collects ever change, update `privacy.html` to match — don't let the
  Privacy Policy drift from what the code actually stores.
- Every `Expense` route filters by the logged-in user's `user_id` (via `current_user_id()`
  in `main.py`) — a row belonging to another user returns `404`, not `403`, so existence
  isn't disclosed. New `Expense`-touching routes must add this filter too; forgetting it is
  the single easiest way to leak one user's financial data to another.
- Request bodies for `/expenses*` are validated via the `ExpenseCreate` SQLModel
  (type + required-field validation from Pydantic). There is no additional server-side
  business validation (e.g. rejecting negative `amount`) — don't assume it exists.
- `.gitignore` already excludes `*.db`, `.env`/`.env.*`, and common secret-bearing paths.
  Never commit the SQLite file or a real secret key; if this project ever needs a `.env`,
  load it with something like `python-dotenv` rather than hardcoding values in `main.py`.

## Before adding anything security-sensitive

- New env vars / secrets: add to `.gitignore` coverage if they live in a file, and never
  print/log them.
- New auth-adjacent code: follow the existing `is_authenticated`/`require_auth` pattern
  above rather than inventing a second mechanism.
- Real user accounts and password hashing have been added (see Auth model above). CSRF
  protection and secret management (`SESSION_SECRET_KEY` is still hardcoded) remain open
  items, unchanged by that work — still demo-only.
