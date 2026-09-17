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

## 2. The `.claude/` Folder — Project Configuration

The `.claude/` folder is where you store Claude Code project configuration. It's checked
into git so your team sees the same setup. Here's what goes where:

```
.claude/
├── CLAUDE.md                    # (optional, usually in repo root instead)
├── settings.json                # Harness configuration (hooks, permissions, etc.)
├── settings.local.json          # Local overrides (git-ignored)
├── rules/                       # Coding conventions & architecture
│   ├── code-style.md           # Language/formatting conventions
│   ├── api-convention.md        # REST/API contract & design
│   ├── security.md              # Security checklist & threat model
│   ├── testing.md               # Testing strategy & patterns
│   └── git-workflow.md          # Branch naming, commit messages, merge strategy
├── commands/                    # Slash commands (e.g., /test-feature, /ship-feature)
│   ├── git-commit.md
│   ├── code-review-feature.md
│   ├── test-feature.md
│   └── ship-feature.md
├── skills/                      # Custom skills (packaged workflows)
│   └── frontend-design/
│       └── SKILL.md
├── agents/                      # Custom subagents (multi-agent workflows)
│   ├── quality-reviewer.md
│   ├── security-reviewer.md
│   └── test-writer.md
├── hooks/                       # Harness hooks (auto-run on tool use)
│   ├── check-black-formatting.py   # Post-write hook: auto-format Python
│   └── README.md                    # How hooks work
└── specs/                       # Feature specs & design docs
    └── 04-refund-policy.md
```

### `rules/` — Encode Project Conventions

Create one `.md` file per topic (code style, API design, security, testing, git workflow).
These are imported at the top of CLAUDE.md with `@rules/filename.md` so Claude reads them
every session without needing to re-explain.

**Example:** `rules/code-style.md`
```markdown
# Code Style

- Python: black formatter, line-length 100
- Naming: snake_case functions, PascalCase classes
- Type hints everywhere (including -> None)
- No docstrings unless the WHY is non-obvious
```

### `settings.json` — Harness Hooks & Automation

Configure automatic checks that run after Claude makes changes. This repo uses a
post-write hook to run `black` on all Python files:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "uv run python .claude/hooks/check-black-formatting.py"
          }
        ]
      }
    ]
  }
}
```

**Use cases for hooks:**
- Auto-format code after writes (black, prettier, gofmt)
- Run linters to catch issues early
- Block destructive commands on protected files
- Enforce file naming conventions
- Pre-commit checks (before you have to fix them manually)

### `commands/` & `skills/` — Reusable Workflows

**Commands** (e.g., `/test-feature`, `/ship-feature`) are packaged sets of instructions
that Claude follows step-by-step. Use them when you have a repeatable workflow:

- `test-feature` → run tests for a feature, report coverage
- `ship-feature` → check branch, run tests, create PR, merge
- `code-review-feature` → run code review on a specific feature

**Skills** are similar but are designed to be reusable across projects. Use a skill when
the workflow is generic enough to share.

**When to create one:**
- You notice you're repeating the same steps manually
- Multiple team members would benefit from the standardization
- The workflow is complex enough that written instructions help

### `agents/` — Multi-Agent Workflows

Define custom subagents that Claude spawns for specialized tasks. Example: `quality-reviewer`
agent that focuses specifically on code readability and patterns, independent from a
`security-reviewer` that checks for vulnerabilities.

Subagents run in parallel, each with focused instructions and tool access. Use them when:
- A task naturally splits into independent reviews (quality, security, performance)
- You want isolation (subagent doesn't see the full codebase context)
- Output from one agent should feed into the next (pipeline)

### `hooks/` — Automatic Enforcement

Store hook scripts that run automatically on tool use. This repo includes:

**`check-black-formatting.py`** — Runs after Write/Edit on `.py` files:
1. Checks if black formatting is needed
2. Auto-formats if issues found
3. Reports result

This prevents improperly formatted code from accumulating.

---

## 3. Permissions & Security

Claude Code prompts for permission before running tools that could affect your code or
system. Understand the modes so you're not constantly approving or overly permissive.

**Permission modes** (via `/config`):

- **`strict`** — Prompt on every tool call. Safest, but tedious for large projects.
- **`standard`** (default) — Prompt on risky operations (destructive, external, shared).
  Approve reversible/local actions freely (reads, edits, test runs).
- **`permissive`** — Approve most actions, prompt only on destructive or shared operations.

**Best practice:** Start with `standard`. Use it for production/shared repos. For
personal/learning projects, `permissive` is fine.

**Common approvals to grant freely:**
- Read files (safe to inspect)
- Edit/Write (reversible, local)
- Running tests (safe feedback loop)
- Git operations on feature branches (not `master`)

**Always prompt on:**
- Destructive commands (`git reset --hard`, `rm -rf`)
- Force push to `master`/`main`
- Deleting files/branches
- External API calls or uploads
- Changes to CI/CD or deploy scripts

**Reducing permission prompts:** Use the `fewer-permission-prompts` skill to scan your
past sessions and auto-allowlist the safe commands you approve most frequently.

---

## 4. Slash Commands & Built-in Features

### Built-in Slash Commands

- **`/config`** — Change model (e.g., switch to Opus), permission mode, or other session
  defaults. Good for quick tweaks without restarting.
- **`/fast`** — Toggle fast mode (faster output, same model). Good for long iterations.
- **`/rename`** — Name the current session something meaningful. Shows up in your session
  history so you can find it later.
- **`/help`** — General Claude Code help and documentation.
- **`/code-review [level]`** — Review the current branch for bugs. Levels: low (quick),
  medium (thorough), high (very thorough), ultra (cloud-based, multi-agent). Can pass
  `--fix` to auto-apply fixes, `--comment` to post as PR comments.
- **`/simplify`** — Review code for reuse/simplification/efficiency cleanups only
  (not correctness bugs).

### Custom Skills (Project-Specific)

Skills invoked with `/skill-name` are packaged workflows. This project includes:

- **`/git-commit`** — Orchestrates the commit workflow: shows status, diffs, recent commits,
  then guides you through writing and committing with proper attribution.
- **`/test-feature`** — Run tests for a specific feature and report coverage.
- **`/ship-feature`** — End-to-end: validate branch, run tests, create/merge PR.
- **`/code-review-feature`** — Code review for a specific feature with detailed findings.
- **`/create-spec`** — Generate a feature spec from a high-level description.

Use skills as your primary interface when a repeatable workflow exists — it's more guided
than free-form chat.

### Shell Access

- **One-off bash:** Type `!` at the start of your input to run a single shell command
  (e.g., `!git status`). Output appears inline.
- **Explicit request:** Ask Claude to run shell commands in plain language and it will use
  the Bash tool to execute them.
- **Avoid interactive commands** with `!` (e.g., `git rebase -i`, `git add -i`) — these
  require user input which isn't supported.

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

## 5. Working with Claude Code Effectively

### Frame Your Requests Clearly

Claude works best with complete context. When starting a task:

1. **State the goal** (not the steps): "Add a user profile page" not "create a new route"
2. **Provide constraints**: "Keep it under 200 LOC", "use the existing auth pattern"
3. **Reference the relevant rules**: "Follow the patterns in `rules/code-style.md`"
4. **Paste code snippets or error messages** when relevant — don't make Claude guess

### Use CLAUDE.md as a Reference Manual

Before diving into a new topic, point Claude at the relevant rule file:
- "Look at `rules/api-convention.md` and build a new endpoint for..."
- "Following `rules/testing.md`, write tests for..."

This saves explanation time and ensures consistency.

### Verify Before You Commit

Always ask Claude to test/verify before committing, especially for:
- Behavioral changes (run the app, try the feature)
- Tests (run the test suite, check coverage)
- Refactors (make sure nothing broke)
- Migrations (test in both directions)

Use `/code-review` when you want a second opinion on code quality before merging.

### Keep Sessions Focused

One session = one feature or fix. When a session grows beyond 20-30 exchanges:
- Commit your work
- Start a fresh session on the next task
- This keeps Claude's context sharp and makes your git history cleaner

### Collaborate on Complex Decisions

For architectural or big-picture changes:
- **Don't ask:** "What should I do?" (too open-ended)
- **Do ask:** "Should I use approach A (pros: X, cons: Y) or approach B (pros: Z, cons: W)?"
  Include your own thinking so Claude can build on it.
- **Then ask:** "Which tradeoff matters more for this project?"

### Import Rules for Consistency

At the top of CLAUDE.md, import rule files so they're loaded every session:

```markdown
# CLAUDE.md

This project uses:
@rules/code-style.md
@rules/api-convention.md
@rules/security.md
```

Claude will read these automatically and apply them without being asked twice.

## 6. Project Structure Conventions

- **`database/`** — SQLite or other persistent state. Contents are git-ignored, but the
  folder structure is documented in code. Paths use `Path(__file__).parent / "database"`.
- **`templates/` or `src/`** — Source code (no compiled artifacts). What gets deployed.
- **`static/`** — CSS, JS, images. Served statically.
- **`.claude/`** — Configuration, rules, hooks. Checked in, shared across the team.
- **`.gitignore`** — Comprehensive: venvs, secrets, build output, OS files, DB files.

Don't mix build artifacts with source. Don't commit `.env`, `node_modules/`, or `*.db`
files.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

**Summary:** You can use, modify, and distribute this code freely (commercially or
otherwise) as long as you include the license and copyright notice.

**Proper attribution when sharing:**
- Link to this repo
- Include the LICENSE file
- Note the original author (Shubham Nagrare, 2026)

**When to add a license to your own project:**
- Before pushing to GitHub for the first time
- Popular choices: MIT (permissive), Apache 2.0 (permissive + patent), GPL (copyleft)
- Update the copyright year and author name
- Add `LICENSE` file to `.gitignore` only if it's generated (most licenses are checked in)


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

---

## How to Use This Repo as a Learning Resource

### For Learning Claude Code

1. **Explore the `.claude/` folder** — This is the core. See how a real project structures:
   - Rules that encode conventions (so they're enforced every session)
   - Hooks that run automatically (no manual linting!)
   - Skills/commands that automate workflows
   - Settings that control behavior

2. **Read CLAUDE.md** — This is the contract between you and Claude. It's referenced at the
   top with `@rules/...` imports so Claude reads it every session.

3. **Check the commit history** — Each commit demonstrates a pattern:
   - Feature branches (e.g., `feature/user-accounts`)
   - Focused commits (one thing per commit)
   - Clear commit messages explaining WHY

4. **Try the slash commands** — Run `/git-commit`, `/ship-feature`, etc. to see how Claude
   follows structured workflows. These show automation in action.

### For Building Your Own Project

1. **Copy `.claude/` wholesale** — Don't start from scratch. The rules, hooks, and settings
   are generic enough to adapt to any language/framework.

2. **Update CLAUDE.md** — Replace the app-specific sections with yours. Keep the
   conventions sections.

3. **Add your own rules** — Create `rules/your-topic.md` for anything specific to your
   stack (e.g., `rules/go-style.md`, `rules/react-patterns.md`).

4. **Customize hooks** — The black-linting hook is an example. Add your own post-write or
   pre-push hooks for your tech stack.

5. **Commit early and often** — Don't wait until "done". Small commits make debugging
   easier and your git history more useful for your team.

### For Teams

When onboarding new developers:

1. Point them to CLAUDE.md and the `.claude/` folder first
2. Explain that Claude Code reads these automatically
3. They don't need to re-explain conventions — Claude already knows them
4. Consistency emerges naturally from the rules, not from repeated instructions

This saves enormous amounts of time compared to explaining conventions in chat repeatedly.

---

## Common Patterns in This Repo

### Pattern: Rules Imported at Session Start

```markdown
# CLAUDE.md

@rules/code-style.md
@rules/api-convention.md
@rules/security.md
```

Claude reads these automatically. No need to repeat "use snake_case" in every task.

### Pattern: Auto-formatting via Hook

```json
// .claude/settings.json
"PostToolUse": [
  {
    "matcher": "Write|Edit",
    "command": "uv run python .claude/hooks/check-black-formatting.py"
  }
]
```

After Claude writes Python, black runs automatically. No "remember to format" nagging.

### Pattern: Skills for Repeatable Workflows

Instead of explaining steps every time, create a skill:

```bash
/ship-feature   # orchestrates: validate → test → PR → merge
/test-feature   # runs tests and reports coverage
/git-commit     # guided commit workflow with proper messages
```

This makes the workflow visible and repeatable.

### Pattern: Dedicated Spec Files

Complex features get a spec file in `.claude/specs/`:

```markdown
# Feature: Refund Policy

## Goals
- Allow users to request refunds within 30 days

## Scope
- New route: POST /refunds
- New table: Refund
- Email notification on approval

## Out of Scope
- Admin refund dashboard (future)
```

Claude can reference the spec to stay on track across sessions.

---

## Next Steps

1. **Clone or fork this repo** — Use it as a template for new projects.
2. **Read through the `.claude/` folder** — Understand each section.
3. **Try a workflow** — Run `/ship-feature` or `/code-review-feature` to see structured work.
4. **Adapt for your project** — Update CLAUDE.md, rules, and hooks for your stack.
5. **Share with your team** — The `.claude/` config makes collaboration with Claude much
   smoother.
