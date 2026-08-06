---
name: draft-pr
description: Opens a draft pull request on GitHub using the `gh` CLI (never the raw GitHub API), summarizing the branch's commits into the PR body, proposing a title, and assigning it to the current user. Use this whenever the user asks to open a PR, put their branch up for review, create a draft pull request, or invokes /draft-pr — even casual phrasing like "put this up" or "PR this" counts, as long as they're working from a git branch with commits to send.
compatibility: requires the `gh` CLI (authenticated) and a git repository with a GitHub remote
---

# Draft PR

Open a **draft** GitHub pull request for the current branch via `gh pr create`, with a title and body generated from the branch's actual commits, and the current user set as assignee — nothing gets created until the user approves the drafted content.

## Workflow

1. **Confirm the tooling works.** Run `gh auth status`. If `gh` isn't installed or isn't authenticated, stop and tell the user what to run (`gh auth login`) — don't attempt any GitHub-facing command without this working, since every step after this one talks to GitHub.

2. **Orient in the repo.** Run `git branch --show-current`. If it's empty (detached HEAD) or the branch is the same as the repo's default branch, stop — there's no sensible PR to open from here (you can't PR a branch into itself, and a detached HEAD has no branch to push).

3. **Determine the base branch — always ask.** Detect a sensible default with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name` (falls back to parsing `git symbolic-ref refs/remotes/origin/HEAD` if `gh` can't reach the repo yet). Show the detected default as a suggestion, but always confirm the base with the user before proceeding — don't assume it's correct, since stacked PRs and feature-branch-off-feature-branch workflows are common and silently defaulting would target the wrong branch.

4. **Check for an existing PR first.** Run `gh pr list --head <branch> --state open --json number,url,title`. If one already exists, stop and tell the user its number/URL/title, and ask whether they meant to update it instead (`gh pr edit`) rather than open a second one.

5. **Check there's actually something to PR.** Fetch first (`git fetch origin <base>`) so the comparison is against the real remote state, then run `git log origin/<base>..HEAD --oneline`. If it's empty, stop and say so — an empty PR isn't useful to anyone.

6. **Check the branch is pushed — ask before pushing.** Compare the branch's local HEAD against its upstream (`git status -sb` or `git rev-list @{u}..HEAD` if an upstream exists; if there's no upstream at all, the branch has never been pushed). If there are local commits not on the remote, show what would be pushed and ask before running `git push -u origin <branch>` — don't push unasked, since publishing commits to a shared remote is exactly the kind of thing that should be confirmed, not assumed.

7. **Note uncommitted changes without blocking on them.** If `git status --short` shows uncommitted changes, mention them to the user (a PR only reflects what's committed and pushed, so anything uncommitted won't be included) but don't force the user to deal with them here — that's a separate concern from opening the PR, and they may want a follow-up commit later.

8. **Read the commit range.** Run `git log origin/<base>..HEAD --format='%H%n%s%n%n%b%n---'` to get every commit's subject and body in the range. This is what the summary must actually reflect — don't paraphrase from memory or the conversation, read the real commits.

9. **Draft the title.** If there's exactly one commit, its subject (minus any Conventional Commits type/scope prefix, if present) is usually already a good title. For multiple commits, synthesize one concise title that captures the overall change rather than concatenating subjects — think "what would someone scanning a PR list need to know this is about," not "everything that happened." Keep it out of past tense ("Add X", not "Added X").

10. **Draft the body.** Use this structure:
    ```markdown
    ## Summary

    <1-3 sentences on what this PR does and why, synthesized from the commits>

    ## Commits

    - <subject of commit 1>
    - <subject of commit 2>
    - ...
    ```
    List commits in chronological order (oldest first, matching `git log`'s natural reverse-chronological output reversed). If the commits follow Conventional Commits and naturally group (e.g. several `feat` commits plus a `test` commit), it's fine to note that grouping in the summary prose — but don't force a taxonomy onto commits that don't follow one.

11. **Get approval before creating anything.** Show the full draft: title, body, base branch, head branch, and assignee (`@me`, i.e. the authenticated user). Wait for a yes. If the user wants changes to the title, body, or base, redraft and show again.

12. **Create the PR.** Write the body to a temp file rather than passing multi-line markdown through `-b`/`--body` inline (shell-escaping a heredoc through a flag is fragile and easy to mangle) — for example `--body-file <(printf '%s' "$body")` or a real temp file you clean up after. Run:
    ```bash
    gh pr create --draft --base <base> --head <branch> --title "<title>" --body-file <path> --assignee "@me"
    ```
    Always pass `--title` and `--body-file` explicitly — omitting either makes `gh pr create` fall into an interactive prompt, which will hang in a non-interactive session. `gh pr create` prints the PR URL on success; report that URL back to the user as confirmation, don't just say "done."

## Notes

- This skill only ever creates **draft** PRs (`--draft` is not optional here) — if the user wants it marked ready for review, that's a separate explicit action (`gh pr ready`), not something to infer.
- Never use the GitHub REST/GraphQL API directly (`curl`, `octokit`, etc.) for anything this skill does — `gh` handles auth, remote resolution, and API versioning correctly, and using it consistently is the whole point of this skill existing.
- If `git push` is rejected (e.g. the remote has diverged), don't force-push to resolve it — stop and explain the situation to the user; force-pushing on their behalf is not a call to make silently.