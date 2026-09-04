$scriptPath = Join-Path $PSScriptRoot 'consolidate_worktree_history.py'

foreach ($pythonCommand in @('python3', 'python')) {
    $resolvedCommand = Get-Command $pythonCommand -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($resolvedCommand) {
        $probeSucceeded = $false
        try {
            $LASTEXITCODE = $null
            & $resolvedCommand.Source -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' *> $null
            $probeSucceeded = $null -ne $LASTEXITCODE -and $LASTEXITCODE -eq 0
        }
        catch {
            $probeSucceeded = $false
        }
        if ($probeSucceeded) {
            & $resolvedCommand.Source $scriptPath @args
            exit $LASTEXITCODE
        }
    }
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.10 or newer is required; checked python3, then python.'
)
exit 2
