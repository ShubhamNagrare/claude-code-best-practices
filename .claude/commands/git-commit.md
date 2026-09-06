---
description: Stage all current changes, write a meaningful commit message from the diff, and push to the current branch — with guided error recovery (up to 3 attempts)
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git pull:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git remote:*), Bash(git log:*), AskUserQuestion
---

# Commit and push current changes

Stage everything currently unstaged, write one meaningful commit message describing why
the change was made, and push it to this branch's remote — recovering from common
failures by asking which fix to apply, rather than giving up or guessing silently.

## Steps

1. **Survey.** Run `git status` and `git diff` (unstaged) to see what's actually changed.
   If the working tree is clean, say so and stop — don't create an empty commit.
2. **Sanity-check before staging.** Scan the changed/untracked file list for anything that
   looks like a secret (`.env`, `*.pem`, `*.key`, `credentials*`, an obvious API key in a
   diff). If anything looks suspicious, stop and show the user the specific file(s) before
   staging anything — "add all" doesn't mean silently commit a secret.
3. **Stage everything**: `git add -A`.
4. **Write the commit message** from `git diff --staged` — imperative present tense, one
   line explaining *why* the change was made, not a restatement of the diff — matching
   `.claude/rules/git-workflow.md`'s convention. Append the same `Co-Authored-By:` trailer
   every other commit in this repo gets.
5. **Commit**: `git commit -m "<message>"`.
6. **Push** to the current branch's remote:
   ```bash
   git push -u origin "$(git branch --show-current)"
   ```
   (`-u` is a no-op if upstream is already set, and sets it the first time a branch is
   pushed.)
7. Report back the commit hash, the commit message, and the branch pushed to.

## Error recovery (max 3 attempts per failing step)

If `git add`, `git commit`, or `git push` fails, don't retry blindly and don't pick a fix
silently:

1. Show the user the **exact error output**.
2. Work out 2–4 concrete, distinct ways to resolve it, and use **AskUserQuestion** to
   present them as options, with one clearly marked "(Recommended)". The recommended
   option is always the safest/least destructive one — never pre-select or default to a
   destructive option (force-push, `--no-verify`, discarding local changes).
3. Apply whichever option the user picks, then retry the step that failed.
4. If it fails again, repeat from (1) — up to **3 total attempts** for that step. After the
   3rd failure, stop and summarize what was tried and what still needs a human decision.
   Do not loop indefinitely.

**Common cases and their recommended fix** (still ask — never auto-apply):

- *No upstream branch* ("has no upstream branch") → recommended: the `git push -u origin
  <branch>` in step 6 already handles this; if it still fails the remote branch/repo may
  not exist — confirm with the user before creating anything.
- *Push rejected, remote has new commits* → recommended: `git pull --rebase origin
  <branch>`, then retry the push. Force-push is a valid *option* to offer but must never
  be the recommended default, and only runs if the user explicitly picks it.
- *Pre-commit hook failure* (lint/format error) → recommended: fix the actual issue the
  hook flagged (e.g. run the project's formatter) and re-stage — not skip the hook. Only
  offer `--no-verify` as a last, clearly-labeled-as-discouraged option, and only run it if
  the user explicitly chooses it.
- *Commit fails because git identity isn't configured* ("Please tell me who you are") →
  this command must **not** run `git config` itself (never modify git config on the user's
  behalf) — tell the user the exact `git config --global user.name` / `user.email`
  commands to run themselves, then stop and wait for them.
- *Nothing staged / empty diff* → not an error to retry, just report there's nothing to
  commit.

## Allowed tools

- `Bash(git status:*)`, `Bash(git diff:*)`, `Bash(git log:*)`, `Bash(git branch:*)`,
  `Bash(git rev-parse:*)`, `Bash(git remote:*)` — read-only inspection.
- `Bash(git add:*)`, `Bash(git commit:*)`, `Bash(git push:*)`, `Bash(git pull:*)` — the
  actual staging/commit/push/rebase-recovery actions.
- `AskUserQuestion` — to present error-recovery options and get the user's choice instead
  of picking a fix unilaterally.

No file-editing tools are used by this command itself. If a pre-commit hook failure needs
an actual code fix (not just re-staging), that's a separate, explicit follow-up — this
command won't silently start editing source files just to make a hook pass.

## Limitations

- **Always stages everything** (`git add -A`) — by design, per how this command was asked
  for. If you only want to commit *some* of your current changes, don't use this command;
  stage them yourself and ask for a targeted commit instead.
- **Pushes on every successful commit** — this is not a commit-only command. If you want
  to commit without pushing, say so explicitly instead of running this.
- **Does not create or switch branches.** It commits and pushes to whatever branch is
  currently checked out, including `master` — it does not enforce this repo's
  feature-branch convention (`.claude/rules/git-workflow.md`) for you. If you're on
  `master` with real feature work, branch first.
- **Never force-pushes, skips hooks, or edits git config on its own** — those only happen
  if explicitly picked as the fix during error recovery.
- **Caps retries at 3 per failing step** — a bounded, human-in-the-loop recovery loop, not
  an auto-fix-everything mechanism. Some failures (network/auth issues, a remote that needs
  creating, a genuinely broken commit) need a human decision beyond what this command will
  attempt.
