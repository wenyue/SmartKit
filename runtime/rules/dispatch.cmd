: << 'CMDBLOCK'
@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0dispatch.ps1" %*
exit /b %ERRORLEVEL%
CMDBLOCK
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec sh "${SCRIPT_DIR}/dispatch.sh" "$@"
