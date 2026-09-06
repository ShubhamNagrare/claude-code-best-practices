# Spend Tracker (Claude Code Demo Project)

This is a sample project created to demonstrate the power of **Claude Code** and its
different features (permissions, slash commands, hooks, MCP, subagents, marketplace, and
more, as we explore them). The app itself is a small expense tracker — the point of the
repo is the workflow, not the app.

**Getting started:** register an account at `/register`, then log in — there is no shared
demo account.

**Tech stack:** Python, FastAPI, SQLModel (SQLite), Jinja2 templates, vanilla JS/CSS.

**Environment & dependencies:** managed with [uv](https://docs.astral.sh/uv/); declared in
`pyproject.toml`, pinned in `uv.lock`.

**Run it:**

```powershell
uv sync                              # create venv + install deps
uv run uvicorn main:app --reload     # start the dev server
```

Open http://127.0.0.1:8000 — you'll land on the login page.

---

# Claude Code Best Practices

A living reference, updated as we explore more of Claude Code in this project. This is the
main point of the repo — treat it as the checklist/playbook, not the app above.

## Project setup — do this before starting any project

- [ ] `git init` the repo before or immediately after the first meaningful change, so every
      edit is tracked from the start.
- [ ] Add a `.gitignore` before the first commit (venvs, `__pycache__/`, `.env`, DB files,
      build output) so secrets and junk never get staged.
- [ ] Create a `CLAUDE.md` (or confirm one exists) describing project conventions,
      architecture notes, and anything Claude shouldn't need to re-derive every session.
- [ ] Decide dependency/environment tooling up front (e.g. `uv`, `poetry`, `npm`) and pin
      lockfiles — don't let Claude guess package managers mid-task.
- [ ] Set a sensible Claude Code **permission mode** for the kind of work planned (tighter
      for shared/production repos, looser for solo sandboxes) — see `/config`.
- [ ] Add a remote (`git remote add origin ...`) and push early so work isn't only local.
- [ ] Pick a license and record the author/owner (see License section below) before the
      repo is shared publicly.

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

## Splitting rules into `.claude/rules/` and importing them into CLAUDE.md

- Topic-specific conventions (code style, API conventions, security notes, testing,
  git workflow) live as separate files under `.claude/rules/` instead of one giant
  `CLAUDE.md` — easier to find, easier to update one topic without touching the rest.
- `CLAUDE.md` pulls them in with `@path/to/file` import syntax (e.g.
  `@.claude/rules/code-style.md`) — imported files load automatically every session, same
  as `CLAUDE.md` itself, so you don't have to remember to mention them.
- Keep `CLAUDE.md` itself to what's genuinely project-wide (what the repo is, how to run
  it, directory layout, cross-cutting architecture facts) and let the imported rule files
  own their topic in depth — don't duplicate the same convention in both places.

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
| POST   | /register         | Create a new account                  |
| GET    | /logout           | Clear session                         |
| GET    | /dashboard        | Dashboard UI (requires login)         |
| GET    | /terms            | Terms and Conditions                  |
| GET    | /privacy          | Privacy Policy                        |
| POST   | /expenses         | Create an expense                     |
| GET    | /expenses         | List expenses                         |
| GET    | /expenses/{id}    | Get a single expense                  |
| PUT    | /expenses/{id}    | Update an expense                     |
| DELETE | /expenses/{id}    | Delete an expense                     |
| GET    | /summary          | Total spend + breakdown by category   |

</details>
