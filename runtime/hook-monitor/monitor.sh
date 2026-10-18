#!/bin/sh
# Source from a Hook launcher before its Python preflight; preserve its exit status.
smartkit_hook_now() {
    if [ "$smartkit_hook_clock" = date ]; then
        date +%s%N 2>/dev/null
    else
        python -c 'import time; print(int(time.monotonic() * 1000000000))' 2>/dev/null
    fi
}

smartkit_hook_clock=date
smartkit_hook_started_ns=$(smartkit_hook_now) || smartkit_hook_started_ns=
case "$smartkit_hook_started_ns" in
    *[!0-9]*|'')
        # BSD date lacks nanoseconds; use the Hook's existing Python prerequisite.
        smartkit_hook_clock=python
        smartkit_hook_started_ns=$(smartkit_hook_now) || smartkit_hook_started_ns=
        ;;
esac

smartkit_hook_report_duration() {
    smartkit_hook_original_status=$1
    smartkit_hook_finished_ns=$(smartkit_hook_now) || smartkit_hook_finished_ns=
    case "$smartkit_hook_started_ns:$smartkit_hook_finished_ns" in
        *[!0-9:]*|:*|*:) return "$smartkit_hook_original_status" ;;
    esac
    smartkit_hook_elapsed_ns=$((smartkit_hook_finished_ns - smartkit_hook_started_ns))
    if [ "$smartkit_hook_elapsed_ns" -gt 200000000 ]; then
        printf '[smartkit] WARNING: %s Hook took %s ms (threshold 200 ms); duration warning only.\n' \
            "$smartkit_hook_name" "$((smartkit_hook_elapsed_ns / 1000000))" >&2 || :
    fi
    return "$smartkit_hook_original_status"
}

trap 'smartkit_hook_report_duration "$?"' 0
