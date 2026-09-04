$scriptPath = Join-Path $PSScriptRoot 'timing.py'

$pythonCommands = @('python3', 'python')
foreach ($pythonCommand in $pythonCommands) {
    $pythonExecutable = Get-Command $pythonCommand -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -ne $pythonExecutable) {
        $pythonPath = $pythonExecutable.Source
        $probeSucceeded = $false
        $LASTEXITCODE = $null
        try {
            & $pythonPath -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' *> $null
            $probeSucceeded = $LASTEXITCODE -eq 0
        }
        catch {
            continue
        }
        if ($probeSucceeded) {
            & $pythonPath $scriptPath @args
            exit $LASTEXITCODE
        }
    }
}

[Console]::Error.WriteLine('ERROR: Python 3.10 or newer is required; checked python3, then python.')
exit 2
