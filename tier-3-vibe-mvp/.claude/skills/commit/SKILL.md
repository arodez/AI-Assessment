---
name: commit
description: Generates well-formatted git commit messages following the Conventional Commits standard (feat/fix/docs/refactor/etc.) from the currently staged diff, then commits after the user approves. Use this whenever the user asks to commit changes, write or draft a commit message, summarize a staged diff, wrap up their work with a commit, or invokes /commit — even if they phrase it casually like "commit this" or "check this in" without naming Conventional Commits explicitly.
compatibility: requires the git CLI, run from inside a git repository
---

# Git Commit

Turn the currently staged (or about-to-be-staged) changes into one or more clean, Conventional Commits-formatted commits, with the user approving the message before anything is actually committed.

## Workflow

1. **See what's there.** Run `git status --short` to see staged, unstaged, and untracked files at a glance, plus `git branch --show-current` so you know what you're committing to.

2. **Handle the nothing-staged case.** If `git diff --cached` is empty but `git status` shows unstaged or untracked changes, don't just stage everything — show the user what's sitting there and ask what to stage (all of it, specific files, or abort). Silently running `git add -A` can sweep in scratch files, debug output, or half-finished work the user didn't mean to commit.

3. **Read the staged diff.** Run `git diff --cached` (add `--stat` first if the diff is large, to orient yourself before reading the full thing). This is what the commit message must actually describe — don't infer intent from the conversation alone, the diff is the source of truth.

4. **Check for anything that shouldn't be committed.** Skim the staged paths and diff content for things like `.env` files, private keys, credentials files, or diff hunks that look like API keys/tokens/passwords. If you spot something that looks like a secret, stop and confirm with the user before drafting a message or committing — this is one of the few git mistakes that's genuinely hard to undo cleanly.

5. **Decide if this is one commit or several.** Look at whether the staged changes tell one coherent story or several unrelated ones (e.g., a bug fix bundled with an unrelated formatting pass, or changes to two unrelated features). When they're unrelated, don't force them into one message with an "and" in it — propose splitting into separate commits instead, and show the user the proposed grouping (which files/hunks go where) before touching anything. Splitting means selectively staging with `git add <path>` or `git add -p` per group, drafting each commit separately, and committing them one at a time. It's fine to end up with one commit when the changes really are one coherent thing — the goal is commits that are each easy to review and revert on their own, not commits that are artificially small.

6. **Draft the message(s)** using the Commit Message Guidelines below.

7. **Get approval before committing.** Show the drafted message (or, if split, all of them together with which files each covers) and wait for a yes before running anything. If the user asks for changes, redraft and show again — don't commit on a guess.

8. **Commit.** For a subject-only message: `git commit -m "type(scope): description"`. For a message with a body, use multiple `-m` flags (`-m "subject" -m "body"`) or a heredoc so the body's line breaks survive — don't jam a multi-line message into a single `-m` string. After each commit, check `git show --stat` against what you intended (not just the command's own summary line) — this catches the two git commit pitfalls below before they compound across a split.

   When splitting into several commits (step 5), `git commit -- <pathspec>` reads the **current working tree** for those paths, not whatever was already staged. If something regenerates a file you meant to delete between staging and committing (a stray OS file like `.DS_Store`, a build artifact), the pathspec commit will silently record it as modified instead of deleted — verify each split commit's diff actually matches what you showed the user before moving to the next one.

   If a split commit needs fixing after the fact, amend it with the same explicit pathspec you created it with (`git commit --amend -- <pathspec>`), never a bare `git commit --amend`. With no pathspec, amend replaces the whole commit tree with the *entire current index* — on a split, that silently pulls back in everything still staged for the other commits and collapses them together.

## Commit Message Guidelines

**Subject line:** `<type>(<scope>): <description>`
- Imperative mood: "Add retry logic", not "Added retry logic" or "Adds retry logic" — read it as completing the sentence "If applied, this commit will ___."
- Keep it to 50 characters where you can; treat ~72 as the hard ceiling.
- No period at the end. Lowercase the description unless it starts with a proper noun.
- Scope is optional — use it when the change clearly belongs to one module/area (`fix(auth): ...`) and omit it when the change doesn't map to a single scope. A missing scope beats a misleading one.

**Types:**

| Type | When to use it |
|---|---|
| `feat` | A new capability for the end user |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting, whitespace, semicolons — no code meaning changed |
| `refactor` | Restructuring code without changing behavior |
| `perf` | A change that specifically improves performance |
| `test` | Adding or correcting tests |
| `build` | Build system or external dependency changes (e.g. package.json, Dockerfile) |
| `ci` | CI/CD configuration and scripts |
| `chore` | Routine maintenance that doesn't fit elsewhere |
| `revert` | Reverting a previous commit |

**Body (optional, add when the subject alone doesn't tell the full story):**
- Leave one blank line after the subject.
- Wrap prose at ~72 characters.
- Explain *what changed and why*, not a line-by-line narration of *how* — the diff already shows how. Reach for a body when the motivation isn't obvious from the subject: a non-obvious bug fix, a tradeoff you made, or context a future reader would otherwise have to reconstruct from the diff.
- Skip the body for genuinely self-explanatory changes (a typo fix, a version bump) — a body that just restates the subject is noise.

**Footer (optional):**
- Breaking changes: either put `!` right after the type/scope (`feat(api)!: ...`) or add a `BREAKING CHANGE: <explanation>` footer paragraph — use whichever the codebase already favors, or the footer form if there's no precedent.
- Issue references (`Closes #123`, `Refs #123`): only include these if the user mentions an issue number or one is otherwise evident (e.g. in the branch name) — don't invent one.

## Example

Input diff: adds a retry with exponential backoff to a flaky network call, plus a test for it.

```
feat(client): retry failed requests with exponential backoff

Requests to the ingest endpoint were failing intermittently under
load with no recovery. Retries up to 3 times with exponential
backoff before surfacing the error to the caller.
```
