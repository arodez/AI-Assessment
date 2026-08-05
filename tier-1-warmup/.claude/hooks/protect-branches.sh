#!/bin/bash
# .claude/hooks/protect-branches.sh
# PreToolUse hook: blocks `git push` commands that would push directly to
# main or JavierCA_Solution.
#
# Matched via the `if` filter in settings ("Bash(git push *)"), so this
# script only runs when the Bash command contains a `git push` subcommand.
#
# Note: this only governs Claude Code sessions that load this hook. It does
# not stop a manual `git push` typed directly in a terminal, or a session
# run with hooks disabled. Pair with remote branch protection rules for a
# hard guarantee — this hook isn't a substitute for that.

set -uo pipefail

PROTECTED_BRANCHES=("main" "JavierCA_Solution")

INPUT=$(cat)
COMMAND=$(jq -r '.tool_input.command // ""' <<<"$INPUT")
CWD=$(jq -r '.cwd // "."' <<<"$INPUT")

deny() {
  jq -n --arg reason "$1" '{
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: $reason
    }
  }'
  exit 0
}

is_protected() {
  local candidate="$1"
  for b in "${PROTECTED_BRANCHES[@]}"; do
    [ "$candidate" = "$b" ] && return 0
  done
  return 1
}

# Block pushes that sweep in every branch, protected ones included
if echo "$COMMAND" | grep -qE -- '(^|[[:space:]])--all([[:space:]]|$)|(^|[[:space:]])--mirror([[:space:]]|$)'; then
  deny "Blocked: this push targets all branches (--all/--mirror), which includes protected branches (${PROTECTED_BRANCHES[*]})."
fi

# Pull out positional (non-flag) arguments after "push"
AFTER_PUSH=$(echo "$COMMAND" | sed -E 's/^.*push[[:space:]]*//')
POSITIONAL=()
for tok in $AFTER_PUSH; do
  [[ "$tok" == -* ]] && continue
  POSITIONAL+=("$tok")
done

REFSPEC="${POSITIONAL[1]:-}"   # position 0 is the remote, e.g. "origin"

TARGET=""
if [ -n "$REFSPEC" ]; then
  if [[ "$REFSPEC" == *:* ]]; then
    TARGET="${REFSPEC#*:}"   # local:remote refspec -> take the remote side
  else
    TARGET="$REFSPEC"
  fi
fi

if [ -n "$TARGET" ] && is_protected "$TARGET"; then
  deny "Blocked: direct push to '$TARGET' is not allowed. Push a feature branch and open a PR instead."
fi

# No branch named explicitly (bare `git push` / `git push origin`) — falls
# back to whatever branch is currently checked out
if [ -z "$TARGET" ]; then
  CURRENT=$(git -C "$CWD" branch --show-current 2>/dev/null || echo "")
  if [ -n "$CURRENT" ] && is_protected "$CURRENT"; then
    deny "Blocked: this push would push the current branch '$CURRENT', which is protected. Push a feature branch and open a PR instead."
  fi
fi

exit 0
