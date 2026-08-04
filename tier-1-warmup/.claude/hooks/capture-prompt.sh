#!/bin/bash
# .claude/hooks/capture-prompt.sh
# UserPromptSubmit hook: stashes the prompt so the Stop hook can pair it
# with Claude's response when it builds a log entry.

set -euo pipefail

INPUT=$(cat)

SESSION_ID=$(jq -r '.session_id' <<<"$INPUT")
PROMPT=$(jq -r '.prompt' <<<"$INPUT")
MODE=$(jq -r '.permission_mode // "unknown"' <<<"$INPUT")
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")

PENDING_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/logs/.pending"
mkdir -p "$PENDING_DIR"

jq -n \
  --arg ts "$TIMESTAMP" \
  --arg prompt "$PROMPT" \
  --arg mode "$MODE" \
  '{timestamp: $ts, prompt: $prompt, mode: $mode}' \
  > "$PENDING_DIR/${SESSION_ID}.json"

exit 0

