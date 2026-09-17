---
description: Stage all current changes, write a meaningful commit message from the diff, sync with master, and push to the current branch — with guided error recovery (up to 3 attempts)
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git push:*), Bash(git pull:*), Bash(git fetch:*), Bash(git merge:*), Bash(git branch:*), Bash(git rev-parse:*), Bash(git remote:*), Bash(git log:*), Read, Edit, AskUserQuestion
---

# Commit and push current changes

Stage everything currently unstaged, write one meaningful commit message describing why
the change was made, sync with `master` so the push doesn't go out stale, and push it to
this branch's remote — recovering from common failures by asking which fix to apply,
rather than giving up or guessing silently.

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
6. **Sync with `master` before pushing** (this repo's main branch — see
   `.claude/rules/git-workflow.md`):
   ```bash
   git fetch origin master
   ```
   - If the current branch **is** `master`, fast-forward it: `git pull origin master`.
   - Otherwise (a feature/fix branch), bring master's latest into the branch:
     `git merge origin/master --no-edit`. This is a merge, not a rebase — it keeps history
     honest about what actually happened and avoids needing a force-push afterward.
   - If this reports "Already up to date," there's nothing to do — continue.
   - If it produces a merge conflict, that's handled under Error recovery below — don't
     resolve conflicts silently.
7. **Push** to the current branch's remote:
   ```bash
   git push -u origin "$(git branch --show-current)"
   ```
   (`-u` is a no-op if upstream is already set, and sets it the first time a branch is
   pushed.)
8. Report back the commit hash, the commit message, whether anything came in from
   `master`, and the branch pushed to.

## Error recovery (max 3 attempts per failing step)

If `git add`, `git commit`, the `master` sync, or `git push` fails, don't retry blindly and
don't pick a fix silently:

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
  <branch>` in step 7 already handles this; if it still fails the remote branch/repo may
  not exist — confirm with the user before creating anything.
- *Merge conflict syncing with `master`* (step 6) → recommended: show the conflicting
  file(s) (`git status`) and resolve them properly (edit out the conflict markers, keeping
  the intent of both sides), then `git add` the resolved files and `git commit` to finish
  the merge before continuing to push. Offer `git merge --abort` (stop, go back to
  pre-sync state, push skipped) as the safe way out if the user doesn't want to resolve it
  right now. Never resolve a real conflict by blindly taking "ours" or "theirs" without
  looking at what it actually discards.
- *Push rejected, remote has new commits* → this should be rare now that step 6 syncs with
  `master` first, but can still happen (another push landed in between, or the current
  branch's own upstream — not `master` — moved). Recommended: `git pull --rebase origin
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
- `Bash(git add:*)`, `Bash(git commit:*)`, `Bash(git push:*)`, `Bash(git pull:*)`,
  `Bash(git fetch:*)`, `Bash(git merge:*)` — the actual staging/commit/master-sync/push/
  rebase-recovery actions.
- `AskUserQuestion` — to present error-recovery options and get the user's choice instead
  of picking a fix unilaterally.
- `Read`, `Edit` — used **only** to resolve merge-conflict markers left by step 6's
  `master` sync, and only after the user picks "resolve conflicts" during error recovery.
  Not used for anything else — a pre-commit hook failure needing a real code fix (not just
  re-staging) is a separate, explicit follow-up, not something this command does on its
  own initiative.

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
- **Syncs with `master` specifically**, via a merge (not rebase), before every push — if
  this repo's main branch is ever renamed, update the hardcoded `master` references in
  this command. Merge conflicts are never auto-resolved; they always go through the same
  AskUserQuestion recovery flow as any other failure.
- **Caps retries at 3 per failing step** — a bounded, human-in-the-loop recovery loop, not
  an auto-fix-everything mechanism. Some failures (network/auth issues, a remote that needs
  creating, a genuinely broken commit) need a human decision beyond what this command will
  attempt.
