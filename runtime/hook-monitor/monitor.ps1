function Write-SmartKitHookDuration {
    param([string]$Name, [System.Diagnostics.Stopwatch]$Timer)
    # Diagnostics, including a closed stderr, must not replace the Hook outcome.
    try {
        if ($Timer.Elapsed.TotalSeconds -gt 0.2) {
            [Console]::Error.WriteLine((
                '[smartkit] WARNING: {0} Hook took {1:F1} ms (threshold 200 ms); duration warning only.' -f
                $Name, $Timer.Elapsed.TotalMilliseconds
            ))
        }
    }
    catch { }
}
