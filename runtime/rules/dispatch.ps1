$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'dispatch.py'

$resolved = Get-Command python -CommandType Application -ErrorAction SilentlyContinue |
    Select-Object -First 1
$pythonReady = $false
if ($null -ne $resolved) {
    try {
        & $resolved.Source -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' *> $null
        $pythonReady = $LASTEXITCODE -eq 0
    }
    catch {
        $pythonReady = $false
    }
}
if ($pythonReady) {
    & $resolved.Source $scriptPath @args
    exit $LASTEXITCODE
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.8 or newer is required; checked python.'
)
exit 2
