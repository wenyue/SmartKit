#!/usr/bin/env sh
set -eu

script_dir=${0%/*}
if [ "$script_dir" = "$0" ]; then
  script_dir=.
fi
script_dir=$(CDPATH= cd -- "$script_dir" && pwd)

for python_command in python3 python; do
  if command -v "$python_command" >/dev/null 2>&1 &&
    "$python_command" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' \
      >/dev/null 2>&1
  then
    exec "$python_command" "$script_dir/worktree_transfer.py" "$@"
  fi
done

echo 'ERROR: Python 3.10 or newer is required; checked python3, then python.' >&2
exit 2
