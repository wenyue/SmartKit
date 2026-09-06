#!/bin/sh

set -u

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if command -v python >/dev/null 2>&1 &&
  python -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' >/dev/null 2>&1
then
    python "$script_dir/check_recommended_tools.py" "$@"
    status=$?
    if [ "${1:-}" = "hook" ]; then
      exit 0
    fi
    exit "$status"
fi

echo 'ERROR: Python 3.8 or newer is required; checked python.' >&2
if [ "${1:-}" = "hook" ]; then
  harness=
  delivery=native
  previous=
  for argument in "$@"; do
    if [ "$previous" = "--harness" ]; then
      harness=$argument
    elif [ "$previous" = "--delivery" ]; then
      delivery=$argument
    fi
    previous=$argument
  done
  case "$harness:$delivery" in
    codex:*)
      printf '%s\n' '{"continue":true,"systemMessage":"ERROR: Python 3.8 or newer is required; checked python."}'
      ;;
    cursor:context)
      printf '%s\n' '{"additional_context":"ERROR: Python 3.8 or newer is required; checked python."}'
      ;;
    cursor:*)
      printf '%s\n' '{"continue":false,"user_message":"ERROR: Python 3.8 or newer is required; checked python."}'
      ;;
    *)
      printf '%s\n' '{"additionalContext":"ERROR: Python 3.8 or newer is required; checked python."}'
      ;;
  esac
  exit 0
fi
exit 2
