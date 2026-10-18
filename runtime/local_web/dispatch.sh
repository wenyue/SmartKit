#!/bin/sh

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
smartkit_hook_name=local-web
if [ "${1:-}" = hook ]; then
    . "$script_dir/../hook-monitor/monitor.sh"
fi

if command -v python >/dev/null 2>&1 &&
  python -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' >/dev/null 2>&1
then
    python "$script_dir/__main__.py" "$@"
    exit $?
fi

echo 'ERROR: Python 3.8 or newer is required; checked python.' >&2
[ "${1:-}" != hook ] || exit 0
exit 2
