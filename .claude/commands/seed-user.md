---
description: Register a random demo user with sample expenses in the local dev database, for manual dashboard testing
allowed-tools: Bash(curl:*), Bash(uv run python:*)
---

# Seed a demo user

Populate the local dev database with one freshly registered user and a handful of random
sample expenses, so the dashboard has something to look at without registering by hand
every time.

## Steps

1. Confirm the dev server is reachable at `http://127.0.0.1:8000`:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/login
   ```
   If this doesn't return `200`, stop and tell the user to start it first with
   `uv run uvicorn main:app --reload` — do not try to start the server yourself.

2. Run the following with `uv run python -c "..."` (stdlib only, no new dependency) to
   generate a random user, register it, log in, and add a handful of random expenses —
   entirely through the app's own running HTTP routes, never by writing to the SQLite file
   directly. `/register`/`/login`/`/expenses` are the only source of truth for this data,
   per `.claude/rules/api-convention.md`, so seeded data gets the exact same validation,
   password hashing, and per-user scoping a real signup would get.

   ```python
   import json, random, string
   import urllib.request, urllib.parse, http.cookiejar
   from datetime import date, timedelta

   BASE = "http://127.0.0.1:8000"
   suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
   username = f"demo_{suffix}"
   email = f"{username}@example.com"
   password = "".join(random.choices(string.ascii_letters + string.digits, k=12))

   jar = http.cookiejar.CookieJar()
   opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

   def post_form(path, fields):
       data = urllib.parse.urlencode(fields).encode()
       opener.open(urllib.request.Request(BASE + path, data=data, method="POST"))

   def post_json(path, payload):
       data = json.dumps(payload).encode()
       req = urllib.request.Request(
           BASE + path, data=data, method="POST",
           headers={"Content-Type": "application/json"},
       )
       opener.open(req)

   post_form("/register", {"username": username, "email": email, "password": password})
   post_form("/login", {"username": username, "password": password})

   CATEGORIES = ["Food", "Transport", "Utilities", "Entertainment", "Shopping"]
   TITLES = {
       "Food": ["Groceries", "Coffee", "Lunch"],
       "Transport": ["Gas", "Bus pass", "Rideshare"],
       "Utilities": ["Electric bill", "Internet", "Water bill"],
       "Entertainment": ["Movie tickets", "Streaming subscription", "Concert"],
       "Shopping": ["New shoes", "Book", "Home decor"],
   }

   expenses = []
   for _ in range(random.randint(4, 6)):
       category = random.choice(CATEGORIES)
       expense = {
           "title": random.choice(TITLES[category]),
           "amount": round(random.uniform(5, 200), 2),
           "category": category,
           "spent_on": str(date.today() - timedelta(days=random.randint(0, 30))),
       }
       post_json("/expenses", expense)
       expenses.append(expense)

   print(json.dumps({
       "username": username, "email": email, "password": password, "expenses": expenses,
   }))
   ```

3. Parse the JSON the script printed and show the user a clean summary directly in the
   terminal — don't just dump the raw JSON:
   - Username, email, and password (this is the only place the plaintext password is ever
     shown — it's stored bcrypt-hashed and cannot be retrieved again after this).
   - The list of expenses that were added (title, category, amount, date).
   - A one-line reminder: log in at `/login` with these credentials to see them on the
     dashboard.

## Allowed tools

- `Bash(curl:*)` — only to confirm the dev server is up before doing anything else.
- `Bash(uv run python:*)` — to run the seed script above inside the project's own Python
  environment. Stdlib only; no new dependency is added for this.

No file-editing or direct-database tools are used — every value is created by driving the
already-running app's real `/register`, `/login`, and `/expenses` routes.

## Limitations

- **Requires the dev server already running** at `http://127.0.0.1:8000` (e.g.
  `uv run uvicorn main:app --reload`). This command does not start it for you.
- **Local dev only** — the base URL is hardcoded to `127.0.0.1:8000`; never point this at a
  deployed environment.
- **No cleanup.** Every run creates a brand-new user and leaves it in
  `database/spend_tracker.db` permanently. There's no undo — delete the dev DB file
  yourself for a clean slate.
- **The password is shown once, in plaintext, in your terminal**, then never again. Treat
  every account this creates as a disposable local test account, never a real credential.
- **Data is for visual testing only** — titles/categories come from a small fixed list and
  aren't representative of real spending patterns.
