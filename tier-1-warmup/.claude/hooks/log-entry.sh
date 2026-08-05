#!/bin/bash
# .claude/hooks/log-entry.sh
# Stop hook: pairs the stashed prompt with Claude's last message, drafts
# Highlights/Limitations/Follow-up with a lightweight Claude call, and
# appends a "## Prompt N" entry to the session log.
#
# Caveats:
# - Model is best-effort: parsed from the transcript JSONL, which is an
#   undocumented internal format and can break across Claude Code versions.
# - This makes one extra `claude -p` call per turn (cost + latency).
# - The /context section is still manual — paste it in yourself.

set -uo pipefail

INPUT=$(cat)

STOP_ACTIVE=$(jq -r '.stop_hook_active // false' <<<"$INPUT")
[ "$STOP_ACTIVE" = "true" ] && exit 0   # avoid double-logging on continuations

SESSION_ID=$(jq -r '.session_id' <<<"$INPUT")
TRANSCRIPT=$(jq -r '.transcript_path' <<<"$INPUT")
OUTCOME=$(jq -r '.last_assistant_message // ""' <<<"$INPUT")
MODE=$(jq -r '.permission_mode // "unknown"' <<<"$INPUT")

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"
PENDING_FILE="$PROJECT_DIR/.claude/logs/.pending/${SESSION_ID}.json"
LOG_FILE="$PROJECT_DIR/session-log.md"

[ -f "$PENDING_FILE" ] || exit 0   # nothing captured for this turn

PROMPT=$(jq -r '.prompt' "$PENDING_FILE")
TIMESTAMP=$(jq -r '.timestamp' "$PENDING_FILE")
[ "$MODE" = "unknown" ] && MODE=$(jq -r '.mode' "$PENDING_FILE")

# Best-effort model lookup from the transcript (undocumented format —
# falls back to "unknown" if parsing fails or the field isn't there)
MODEL=$(jq -rs 'map(select(.type=="assistant")) | last | .message.model // "unknown"' \
  "$TRANSCRIPT" 2>/dev/null || echo "unknown")

# Repo / branch, best-effort
cd "$PROJECT_DIR" 2>/dev/null || true
REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null || echo "$PROJECT_DIR")")
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Draft the reflective fields with a separate, lightweight headless call.
# IMPORTANT: --settings disables hooks for this nested call only. Without
# it, this call inherits the project's own hooks (including this same
# Stop hook) and can trigger itself recursively.
NO_HOOKS_SETTINGS="${CLAUDE_PROJECT_DIR:-.}/.claude/hooks/no-hooks.json"
DRAFT_RAW=$(claude -p --settings "$NO_HOOKS_SETTINGS" --output-format json \
  "Draft a short log entry for a personal engineering log based on this exchange. Reply with ONLY minified JSON, no markdown fences, no commentary: {\"highlights\":\"...\",\"limitations\":\"...\",\"follow_up\":\"...\"}. 1-2 sentences per field, written from the human user's point of view about the AI's output. PROMPT: $PROMPT --- RESPONSE: $OUTCOME" \
  2>/dev/null || echo '{}')

DRAFT_JSON=$(jq -r '.result // "{}"' <<<"$DRAFT_RAW" 2>/dev/null || echo '{}')
HIGHLIGHTS=$(jq -r '.highlights // empty' <<<"$DRAFT_JSON" 2>/dev/null)
LIMITATIONS=$(jq -r '.limitations // empty' <<<"$DRAFT_JSON" 2>/dev/null)
FOLLOWUP=$(jq -r '.follow_up // empty' <<<"$DRAFT_JSON" 2>/dev/null)
[ -z "$HIGHLIGHTS" ] && HIGHLIGHTS="[DRAFT unavailable — fill in manually]"
[ -z "$LIMITATIONS" ] && LIMITATIONS="[DRAFT unavailable — fill in manually]"
[ -z "$FOLLOWUP" ] && FOLLOWUP="[DRAFT unavailable — fill in manually]"

# Create the file with the session-level block if it doesn't exist yet
if [ ! -f "$LOG_FILE" ]; then
  cat > "$LOG_FILE" <<EOF
# Session Log

| Field | Value |
|---|---|
| **Tool** | Claude Code |
| **Repo / Branch** | $REPO / $BRANCH |

---

EOF
fi

# NOTE: `grep -c` prints the match count but exits 1 when that count is 0,
# so chaining `|| echo 0` on it in a single substitution used to concatenate
# both outputs ("0\n0") on the very first entry and break the arithmetic
# below (silently, since we don't use `set -e`) — every turn's entry was
# then lost after the fact by the unconditional `rm -f` further down.
# Split into two statements so grep's exit code never reaches the `||`.
EXISTING_COUNT=$(grep -c '^## Prompt ' "$LOG_FILE" 2>/dev/null)
N=$(( EXISTING_COUNT + 1 ))

cat >> "$LOG_FILE" <<EOF
## Prompt $N

> $PROMPT

### Metadata

| Field | Value |
|---|---|
| **Date/Time** | $TIMESTAMP |
| **Model** | $MODEL |
| **Mode** | $MODE |
| **Session ID** | $SESSION_ID |
| **Tags** |  |
| **Cost / Tokens** |  |

### Outcome

$OUTCOME

### Context

\`\`\`
[paste /context output here]
\`\`\`

### Highlights

- $HIGHLIGHTS [DRAFT — edit me]

### Notable limitations or surprises

- $LIMITATIONS [DRAFT — edit me]

### Follow-up / next steps

- $FOLLOWUP [DRAFT — edit me]

---

EOF

rm -f "$PENDING_FILE"
exit 0
