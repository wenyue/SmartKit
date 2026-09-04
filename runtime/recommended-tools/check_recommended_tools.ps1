$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'check_recommended_tools.py'

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
        $status = $LASTEXITCODE
        if ($args.Count -gt 0 -and $args[0] -eq 'hook') {
            exit 0
        }
        exit $status
    }
}

[Console]::Error.WriteLine(
    'ERROR: Python 3.10 or newer is required; checked python3, then python.'
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
    $message = 'ERROR: Python 3.10 or newer is required; checked python3, then python.'
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
