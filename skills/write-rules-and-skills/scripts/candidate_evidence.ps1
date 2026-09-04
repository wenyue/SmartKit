$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'candidate_evidence.py'

foreach ($pythonName in @('python3', 'python')) {
    $pythonCommand = Get-Command $pythonName -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($null -eq $pythonCommand) {
        continue
    }

    $probeExitCode = 1
    try {
        & $pythonCommand.Source -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' *> $null
        $probeExitCode = $LASTEXITCODE
    }
    catch {
        $probeExitCode = 1
    }
    if ($probeExitCode -eq 0) {
        & $pythonCommand.Source $scriptPath @args
        exit $LASTEXITCODE
    }
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.10 or newer is required; checked python3, then python.'
)
exit 2
