#!/bin/sh
set -u
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
status=2
if command -v python >/dev/null 2>&1 &&
    python -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' >/dev/null 2>&1
then
    python "$script_dir/deep_links.py" "$@"
    status=$?
else
    echo 'SmartKit Links: Python 3.8 or newer is required.' >&2
fi
# The optional link maintenance Hook must not block unrelated session work.
if [ "${1:-}" = 'ensure' ]; then
    for argument in "$@"; do
        if [ "$argument" = '--quiet' ]; then exit 0; fi
    done
fi
exit "$status"
