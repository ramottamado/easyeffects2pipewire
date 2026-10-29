#!/usr/bin/env bash
# PostToolUse hook: lint-fix and format an edited .py file with ruff.
# Exit 2 sends remaining lint errors back to Claude.
f=$(jq -r '.tool_response.filePath // .tool_input.file_path // empty')
case "$f" in *.py) ;; *) exit 0 ;; esac
[ -f "$f" ] || exit 0
cd "$CLAUDE_PROJECT_DIR" || exit 0
uv run -q ruff check --fix -q "$f" >&2 || exit 2
uv run -q ruff format -q "$f" >&2 || exit 2
