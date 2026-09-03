$scriptPath = Join-Path $PSScriptRoot 'timing.py'

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'
    if ($LASTEXITCODE -eq 0) {
        & py -3 $scriptPath @args
        exit $LASTEXITCODE
    }
}

$pythonCommands = @('python3', 'python') + @(
    Get-Command 'python3.*' -CommandType Application -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^python3\.\d+(?:\.exe)?$' } |
        Select-Object -ExpandProperty Source
)
foreach ($pythonCommand in $pythonCommands) {
    if (Get-Command $pythonCommand -ErrorAction SilentlyContinue) {
        & $pythonCommand -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'
        if ($LASTEXITCODE -eq 0) {
            & $pythonCommand $scriptPath @args
            exit $LASTEXITCODE
        }
    }
}

Write-Error 'Python 3.10 or newer is required.'
exit 2
