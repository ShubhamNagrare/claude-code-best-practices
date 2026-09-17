# Claude Code Hooks

This directory contains hook scripts that run automatically during Claude Code operations. These hooks enforce project conventions and ensure code quality.

## Hooks

### `check-black-formatting.py` (Post-Write/Edit)

**Purpose**: Automatically format Python files with black after Claude writes or edits them.

**Trigger**: Runs after any `Write` or `Edit` tool use on Python files (`.py`)

**Behavior**:
1. Receives file path from tool metadata (via stdin)
2. Checks if the file needs formatting using `black --check`
3. If formatting issues exist, runs `black` to auto-format
4. Reports result to stderr

**Line length**: Uses the project's configured black line-length (100 chars, set in `pyproject.toml`)

**Files**: 
- `check-black-formatting.py` — Main hook script (Python, cross-platform)
- `check-black-formatting.ps1` — Alternative PowerShell version (for reference)

## How Hooks Work

Hooks are configured in `.claude/settings.json` under the `hooks` section:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",  // triggers on Write or Edit tools
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

The harness passes tool metadata as JSON via stdin to the hook command, which extracts the file path and processes accordingly.

## Adding New Hooks

To add a new hook:

1. Create a script in this directory (e.g., `my-hook.py`)
2. Ensure it reads JSON from stdin and extracts relevant metadata
3. Add an entry to `.claude/settings.json` under `hooks` with the appropriate matcher and command
4. Test by triggering the hook with a tool call

## Exit Codes

- **0**: Success (always, even if formatting was needed)
- **1**: Error (unexpected exception)

Hooks report results to stderr but do not block tool execution.
