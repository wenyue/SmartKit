$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'check_recommended_tools.py'

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
    $status = $LASTEXITCODE
    if ($args.Count -gt 0 -and $args[0] -eq 'hook') {
        exit 0
    }
    exit $status
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.8 or newer is required; checked python.'
)
if ($args.Count -gt 0 -and $args[0] -eq 'hook') {
    $harness = $null
    $delivery = 'native'
    for ($index = 0; $index -lt $args.Count - 1; $index++) {
        if ($args[$index] -eq '--harness') {
            $harness = $args[$index + 1]
        }
        elseif ($args[$index] -eq '--delivery') {
            $delivery = $args[$index + 1]
        }
    }
    $message = 'ERROR: Python 3.8 or newer is required; checked python.'
    if ($harness -eq 'codex') {
        @{ continue = $true; systemMessage = $message } |
            ConvertTo-Json -Compress | Write-Output
    }
    elseif ($harness -eq 'cursor' -and $delivery -eq 'context') {
        @{ additional_context = $message } | ConvertTo-Json -Compress | Write-Output
    }
    elseif ($harness -eq 'cursor') {
        @{ continue = $false; user_message = $message } |
            ConvertTo-Json -Compress | Write-Output
    }
    else {
        @{ additionalContext = $message } | ConvertTo-Json -Compress | Write-Output
    }
    exit 0
}
exit 2
