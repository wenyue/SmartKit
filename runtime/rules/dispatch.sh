#!/bin/sh

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v python >/dev/null 2>&1 &&
  python -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' >/dev/null 2>&1
then
    exec python "$script_dir/dispatch.py" "$@"
fi

echo 'ERROR: Python 3.8 or newer is required; checked python.' >&2
exit 2
