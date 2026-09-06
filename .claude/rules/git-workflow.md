# Git Workflow

## One feature = one branch

Every new feature or fix gets its own branch off `master` — don't commit new work directly
to `master`. (Note: the first two commits in this repo's history were made directly on
`master`, before this convention existed — that's history, not the pattern to continue.)

```bash
git checkout master
git pull
git checkout -b feature/<short-kebab-description>   # e.g. feature/csv-export
# or: fix/<short-kebab-description> for bug fixes
```

- Branch names are lowercase, hyphen-separated, prefixed by type: `feature/...`, `fix/...`.
- Keep a branch scoped to one feature/fix — don't pile unrelated changes onto it.

## Commit as you go, with relevant messages

- Commit at meaningful checkpoints, not just once at the end of a branch's life.
- Write commit messages that explain **why**, not just what changed — the diff already
  shows what changed. One-line summary in imperative present tense ("Add terms/privacy
  pages", not "Added" or "Adding").
- Commits made by Claude Code in this repo automatically get a `Co-Authored-By:` trailer
  (and a session link) appended — that's expected, don't strip it.
- Never use `--no-verify`, `--no-gpg-sign`, or amend a commit that's already been pushed,
  unless explicitly asked to.

## Push early, push often

Push the feature branch to `origin` as soon as it exists, not just when the feature is
"done" — the branch is your backup:

```bash
git push -u origin feature/<short-kebab-description>   # first push of the branch
git push                                                 # subsequent pushes
```

## Finishing a feature

- Small/solo changes: merge the branch back into `master` locally and push:
  ```bash
  git checkout master
  git pull
  git merge feature/<short-kebab-description>
  git push
  ```
- Anything worth a second look before it lands: open a PR instead of merging locally
  (`gh pr create`), even solo — it gives a review checkpoint and a record of *why* on
  GitHub.
- After merging, delete the feature branch (local and remote) so stale branches don't pile
  up:
  ```bash
  git branch -d feature/<short-kebab-description>
  git push origin --delete feature/<short-kebab-description>
  ```

## Safety

- Never force-push `master`, never `git reset --hard`/`git clean -f` without checking
  `git status` first and confirming with the user — same rule as everywhere else in this
  project, restated here because it's easy to forget mid-branch-cleanup.
- Confirm with the user before pushing, opening PRs, or deleting branches — these are
  visible/hard-to-reverse actions, not silent local edits.
