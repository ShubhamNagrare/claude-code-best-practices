# Claude Code Best Practices Demo

A comprehensive guide to using **Claude Code** effectively in your projects, demonstrated
through a working expense tracker application.

**What this is:** A living reference documenting Claude Code workflows, features, and best
practices as we explore them. The included app (Spend Tracker) is secondary — it exists to
demonstrate practices, not as the deliverable.

**What this isn't:** A production application, a complete MCP reference, or a comprehensive
API spec. It's a playground for learning.

---

## Quick Start

**Demo login:** `username` / `password`

**Tech stack:** Python, FastAPI, SQLModel (SQLite), Jinja2 templates, vanilla JS/CSS

**Setup:**

```powershell
uv sync                              # install dependencies
uv run uvicorn main:app --reload     # start dev server (http://127.0.0.1:8000)
uv run black .                       # format code
```

See [commands in CLAUDE.md](CLAUDE.md) for more.

---

# Claude Code Best Practices Guide

A detailed playbook for working with Claude Code. Start here when setting up a new project,
or reference specific sections as needed.

## 1. Project Setup Checklist

Start here with every new project. These steps set Claude Code up for success.

### Before Writing Code

- [ ] **Initialize git early:** `git init` before or immediately after the first change.
  Every edit should be tracked from the start.
- [ ] **Create `.gitignore`:** Add it before the first commit. Include venvs
  (`__pycache__/`, `node_modules/`, `.venv/`), build output, secrets (`.env`, `.env.*`,
  `*.key`), DB files, and platform files (`.DS_Store`, `Thumbs.db`).
  
  ```gitignore
  # Python
  __pycache__/
  *.pyc
  .venv/
  
  # Secrets & env
  .env
  .env.*
  *.key
  
  # Data
  *.db
  *.sqlite
  database/
  
  # IDE
  .vscode/
  .idea/
  ```

- [ ] **Write CLAUDE.md:** Document project conventions, architecture, tech stack, and
  commands. See [CLAUDE.md](CLAUDE.md) in this repo for an example. This is the single
  most important file — Claude reads it every session and uses it to understand your
  preferences before diving into code.

- [ ] **Set up `.claude/` folder structure** (see next section) with rules, settings, and
  hooks that encode project conventions automatically.

- [ ] **Choose dependency tooling upfront:** Pick one (`uv`, `pip`, `poetry`, `npm`) and
  stick with it. Add a lockfile to `git` so Claude doesn't have to guess versions.

- [ ] **Set a permission mode:** Use `/config` to pick a sensible default for your
  situation (tighter for shared repos, looser for personal sandboxes). This reduces
  permission prompts and makes the workflow smoother.

- [ ] **Add a remote early:** `git remote add origin <url>` and push the initial commit.
  Your work is now backed up and visible to collaborators.

- [ ] **Pick a license before sharing:** Add a `LICENSE` file (this repo uses MIT) and
  update `README.md` with author/copyright info. GitHub shows this on the repo homepage.

## Permissions

- Claude Code prompts for approval on tool calls not already allowed by your permission
  mode or settings. Use `/config` to review/change the default mode.
- Prefer approving narrowly-scoped, reversible actions (edits, local reads, test runs)
  freely, and keep a closer eye on anything destructive, shared, or hard to reverse (force
  push, `git reset --hard`, deleting files/branches).
- The `fewer-permission-prompts` skill can scan past sessions and add a prioritized
  allowlist to `.claude/settings.json` for the read-only commands you approve most often.

## Slash commands

- Slash commands (e.g. `/config`, `/rename`, `/fast`) are built-in CLI verbs — distinct
  from **skills**, which are packaged, repo- or user-defined instruction sets invoked the
  same way (`/skill-name`) but tailored to a specific workflow.
- `/rename` — renames the current session (used to name this one "Landing Page
  Improvement" → now evolved into this best-practices project).
- `/config` — change model, permission mode, and other session defaults.
- `/help` — general Claude Code help.

## Bash / shell access in chat

- Type `!` at the start of the input line to drop into one-off bash mode and run a shell
  command directly in the session (e.g. `!git status`) — output appears inline in the
  conversation. It's per-line, not a persistent mode switch.
- Alternatively, just ask Claude in plain language to run git/shell commands on your
  behalf via its Bash tool.

## Sharing images / design references with Claude

- Pasting an image directly into the CLI prompt doesn't always work depending on your
  terminal. The reliable path: save the file to disk (e.g. `Downloads`), tell Claude the
  filename or folder ("it's in Downloads"), and it can locate and read it.
- Claude can only read files inside the current project's working directory by default —
  if your reference image is elsewhere (e.g. `Downloads`), it will copy it into the repo
  first, then read it from there.

## Visually verifying UI changes (claude-in-chrome)

- After a frontend/design change, ask Claude to actually open it in a browser rather than
  just trusting the code — it can drive Chrome (navigate, click, type, screenshot) via the
  `claude-in-chrome` integration.
- This catches things static review misses: does the chart actually render, do stats
  update after adding data, does the layout hold up after a real interaction (add/delete).
- Good practice for any task involving a visual reference (e.g. "make it look like this
  image") — implement, then screenshot the real running app next to the ask.
- If a browser-driven click *looks* successful but nothing changes on screen, don't trust
  the screenshot alone — cross-check with `read_network_requests` (did the expected
  request actually fire?) and `javascript_tool` (e.g. `element.click()` or checking field
  values directly). Automated clicks can silently miss due to coordinate-scaling mismatches
  or interfering browser extensions; the JS/network layer tells you if the app itself is
  actually broken or if it's just the automation tooling.

## Keeping local state in its own folder

- App state that must persist between runs (SQLite DB files, uploads, caches) should live
  in a dedicated folder (e.g. `database/`) rather than the repo root — keeps the project
  root focused on source, and makes it obvious what's safe to wipe/reset.
- Point the code at that folder with a path relative to the file, not the current working
  directory (e.g. `Path(__file__).parent / "database"`), and create the folder on startup
  if missing — so it works regardless of where the app is launched from.
- Keep the folder's contents git-ignored (a root-level `*.db` pattern already covers files
  inside it) rather than the folder itself, so the structure is documented in code without
  committing local data.

<!--
  Add new subsections here as we explore more features, e.g.:
  ## Hooks
  ## Claude Code Marketplace / Plugins
  ## Subagents
  ## MCP servers
-->

## License

MIT License — see below. Update the author name if this should be attributed differently.

```
MIT License

Copyright (c) 2026 Shubham Nagrare

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## App Reference (minimal — see top of file)

<details>
<summary>Project structure & API endpoints</summary>

```
main.py              # FastAPI app: auth routes, dashboard, expense API
templates/           # Jinja2 templates (login, register, dashboard, terms, privacy)
static/style.css     # App styling
pyproject.toml       # Project metadata and dependencies
uv.lock              # Locked dependency versions
```

| Method | Path              | Description                          |
|--------|-------------------|---------------------------------------|
| GET    | /login            | Login page                            |
| POST   | /login            | Authenticate                          |
| GET    | /register         | Register page                         |
| POST   | /register         | Register (demo, static account)       |
| GET    | /logout           | Clear session                         |
| GET    | /dashboard        | Dashboard UI (requires login)         |
| GET    | /terms            | Terms and Conditions                  |
| GET    | /privacy          | Privacy Policy                        |
| GET    | /refund-policy    | Refund Policy                         |
| POST   | /expenses         | Create an expense                     |
| GET    | /expenses         | List expenses                         |
| GET    | /expenses/{id}    | Get a single expense                  |
| PUT    | /expenses/{id}    | Update an expense                     |
| DELETE | /expenses/{id}    | Delete an expense                     |
| GET    | /summary          | Total spend + breakdown by category   |

</details>
