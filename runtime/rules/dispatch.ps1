$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'dispatch.py'

foreach ($pythonCommand in @('python3', 'python')) {
    $resolved = Get-Command $pythonCommand -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $resolved) {
        continue
    }
    try {
        & $resolved.Source -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' *> $null
    }
    catch {
        continue
    }
    if ($LASTEXITCODE -eq 0) {
        & $resolved.Source $scriptPath @args
        exit $LASTEXITCODE
    }
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.10 or newer is required; checked python3, then python.'
)
exit 2
