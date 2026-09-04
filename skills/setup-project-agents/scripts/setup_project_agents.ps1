$ErrorActionPreference = 'Stop'
$workflow = Join-Path $PSScriptRoot 'workflow.py'

$pythonCommands = @('python3', 'python')
foreach ($pythonCommand in $pythonCommands) {
    $pythonExecutable = Get-Command $pythonCommand -CommandType Application `
        -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($pythonExecutable) {
        $pythonPath = $pythonExecutable.Source
        $pythonProbeExitCode = 1
        $LASTEXITCODE = $null
        try {
            & $pythonPath -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' *> $null
            if ($null -ne $LASTEXITCODE) {
                $pythonProbeExitCode = $LASTEXITCODE
            }
        }
        catch {
            $pythonProbeExitCode = 1
        }
        if ($pythonProbeExitCode -eq 0) {
            & $pythonPath $workflow @args
            exit $LASTEXITCODE
        }
    }
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.10 or newer is required; checked python3, then python.'
)
exit 2
