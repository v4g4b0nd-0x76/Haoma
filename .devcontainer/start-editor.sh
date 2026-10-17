#!/bin/sh
# Start the site editor inside a Codespace. Logs to tools/.editor.log so a
# failed attach is visible in the file tree, not only in a vanished terminal.
set -eu
cd "$(dirname "$0")/.."
mkdir -p tools
export PYTHONUNBUFFERED=1
echo "── $(date -u +%Y-%m-%dT%H:%M:%SZ) starting editor ──" >> tools/.editor.log
exec python3 -u tools/editor.py >> tools/.editor.log 2>&1
