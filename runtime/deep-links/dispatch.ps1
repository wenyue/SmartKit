$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'deep_links.py'
$status = 2
$pythonReady = $false
$resolved = Get-Command python -CommandType Application -ErrorAction SilentlyContinue |
    Select-Object -First 1
if ($null -ne $resolved) {
    try {
        & $resolved.Source -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' *> $null
        $pythonReady = $LASTEXITCODE -eq 0
    }
    # Any probe failure leaves Python unverified; optional quiet maintenance can safely skip registration.
    catch { $pythonReady = $false }
}
if ($pythonReady) {
    & $resolved.Source $scriptPath @args
    $status = $LASTEXITCODE
}
else {
    [Console]::Error.WriteLine('SmartKit Links: Python 3.8 or newer is required.')
}
if ($args.Count -gt 0 -and $args[0] -eq 'ensure' -and $args -contains '--quiet') { exit 0 }
exit $status
