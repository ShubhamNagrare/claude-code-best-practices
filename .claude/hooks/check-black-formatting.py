#!/usr/bin/env python3
"""
Post-Claude hook: Check and auto-format Python files with black
Runs after Claude writes/edits Python files to ensure consistent formatting.
Receives JSON via stdin with tool metadata, extracts the file path, and runs black.
"""

import sys
import json
import subprocess
from pathlib import Path


def main():
    try:
        # Read JSON input from stdin (harness provides tool call metadata)
        data = json.load(sys.stdin)
        file_path = data.get("tool_input", {}).get("file_path", "")

        if not file_path:
            return

        # Only process Python files
        if not file_path.endswith(".py"):
            return

        file_obj = Path(file_path)
        if not file_obj.exists():
            return

        print(f"📋 Checking black formatting: {file_path}", file=sys.stderr)

        # Check if formatting is needed
        check_result = subprocess.run(
            ["uv", "run", "black", "--check", "--quiet", file_path],
            capture_output=True,
        )

        if check_result.returncode != 0:
            # Format the file
            print("⚠️  Formatting issues detected. Running black to fix...", file=sys.stderr)
            subprocess.run(["uv", "run", "black", "--quiet", file_path])
            print("✅ File formatted with black", file=sys.stderr)
        else:
            print("✅ File is properly formatted", file=sys.stderr)

    except Exception as e:
        print(f"❌ Hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
