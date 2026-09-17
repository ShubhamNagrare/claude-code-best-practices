# API Conventions

Conventions for the JSON API in `main.py` (`/expenses*`, `/summary`). Page routes
(`/login`, `/dashboard`, `/terms`, etc.) return HTML and aren't "the API" in this sense.

## Endpoints

| Method | Path              | Auth | Body                | Returns                              |
|--------|-------------------|------|----------------------|----------------------------------------|
| POST   | `/expenses`       | yes  | `ExpenseCreate`       | Created `Expense` (200)               |
| GET    | `/expenses`       | yes  | —                     | `list[Expense]` (200)                 |
| GET    | `/expenses/{id}`  | yes  | —                     | `Expense` (200) or `404`              |
| PUT    | `/expenses/{id}`  | yes  | `ExpenseCreate`       | Updated `Expense` (200) or `404`      |
| DELETE | `/expenses/{id}`  | yes  | —                     | `{"message": "..."}` (200) or `404`   |
| GET    | `/summary`        | yes  | —                     | `{total_spent, by_category}` (200)    |

No versioning prefix (no `/api/v1/...`) — routes are flat off the root. If a breaking
change is ever needed, that's the point to introduce a version prefix; don't add one
speculatively for a single-consumer demo app.

## Auth

- Every endpoint above requires a valid session cookie (set by `POST /login`) — there is
  **no API key / bearer token** auth path. `require_auth(request)` is called as the first
  line of the handler and raises `401` (FastAPI's default `{"detail": "Not authenticated"}`
  body) if the session is missing.
- New endpoints under this API must call `require_auth(request)` the same way. Don't
  introduce a second auth mechanism for "just the API."

## Request / response shape

- Bodies and responses are JSON, matching Python field names exactly — `snake_case`
  throughout (`spent_on`, not `spentOn`). Keep this consistent for any new field.
- **Input model ≠ table model**: request bodies are validated against `ExpenseCreate` (a
  non-table `SQLModel`), not `Expense` directly. This is deliberate — it decouples what a
  client can send from the full DB row shape (e.g. `id` is never client-settable). Any new
  resource should follow the same split: a `<Resource>Create` input schema plus the table
  model for the response.
- Responses that return a full resource use FastAPI's `response_model=` on the route
  decorator (see `create_expense`, `update_expense`) rather than manually serializing.
- `PUT /expenses/{id}` behaves like a **partial update** in practice — it calls
  `expense.model_dump(exclude_unset=True)` and only overwrites fields the client actually
  sent, despite being a `PUT`. Know this nuance before relying on PUT-replaces-everything
  semantics; if you need true full-replace-or-patch distinction later, that's a deliberate
  API change (e.g. add a real `PATCH`), not something to silently alter.

## Status codes and errors

- Success is always `200` — there's no `201 Created` on `POST /expenses` or
  `204 No Content` on `DELETE`. Match this rather than mixing in "more correct" codes for
  just one endpoint; if the whole API's status-code conventions are revisited, do it
  consistently across all endpoints at once.
- Not-found resources raise `HTTPException(status_code=404, detail="Expense not found")`.
  Errors surface as FastAPI's standard `{"detail": "<message>"}` JSON body — don't invent a
  different error envelope for new endpoints.
- Auth failures are `401` with `{"detail": "Not authenticated"}`, via `require_auth`.

## Query parameters

- `GET /expenses` supports optional filtering: `?category=<name>` (exact match). Follow
  this pattern (plain optional query params, exact-match filters) for any new list filters
  rather than introducing a query DSL.
- No pagination on list endpoints (`/expenses` returns the full table). Fine while this is
  a small demo dataset; if pagination is ever added, use `limit`/`offset` (or `skip`) query
  params consistent with typical FastAPI examples, applied to all list endpoints at once —
  not just the one that happens to need it first.

## Dates

- `spent_on` is a `date`, serialized as an ISO `YYYY-MM-DD` string, and defaults to
  "today" server-side (`Field(default_factory=date.today)`) if the client omits it. Any new
  date field should follow the same default-to-today-if-omitted behavior unless there's a
  specific reason not to.

## Client usage

- The only current API consumer is the inline `<script>` in `dashboard.html`, using
  `fetch`. It treats any `401` response as "session expired" and redirects to `/login`
  client-side — repeat that check on any new fetch call against one of these endpoints.
