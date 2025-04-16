param (
    [string]$Username = $null
)

# Get current date and time for log file names
$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"

# Get all processes with owner info
$processes = Get-WmiObject Win32_Process | ForEach-Object {
    $owner = $_.GetOwner()
    $user = if ($owner.ReturnValue -eq 0) { "$($owner.User)" } else { "NO_USER" }

    [PSCustomObject]@{
        User        = $user
        Name        = $_.Name
        PID         = $_.ProcessId
        CPUTime     = $_.KernelModeTime
        MemUsageKB  = $_.WorkingSetSize / 1KB
    }
}

# Only filter by username if one is provided
if ($Username) {
    $processes = $processes | Where-Object { $_.User -ieq $Username }
}

# Group processes by user (after filtering if needed)
$grouped = $processes | Group-Object -Property User

# Store log file paths
$logFiles = @()

foreach ($group in $grouped) {
    $user = $group.Name
    $filename = "$user-process-log-$timestamp.txt"
    $filepath = Join-Path $env:TEMP $filename

    $content = @()
    $content += "Date: $(Get-Date -Format 'yyyy-MM-dd')"
    $content += "Time: $(Get-Date -Format 'HH:mm:ss')"
    $content += ""

    foreach ($proc in $group.Group) {
        $content += "Process Name : $($proc.Name)"
        $content += "Process PID  : $($proc.PID)"
        $content += "CPU Time     : $($proc.CPUTime)"
        $content += "Memory (KB)  : $([math]::Round($proc.MemUsageKB, 2))"
        $content += ""
    }

    $content | Out-File -FilePath $filepath -Encoding UTF8
    $logFiles += $filepath
}

# Open all logs in notepad
$notepadProcs = @()
foreach ($file in $logFiles) {
    $np = Start-Process notepad.exe $file -PassThru
    $notepadProcs += $np
}

Write-Host "Logs opened in Notepad. Press Enter to close all Notepad windows and finish..."
[void][System.Console]::ReadLine()

# Close all Notepad instances opened by script
foreach ($np in $notepadProcs) {
    try {
        $np.CloseMainWindow() | Out-Null
        Start-Sleep -Milliseconds 500
        if (!$np.HasExited) {
            $np.Kill()
        }
    } catch {
        Write-Warning "Could not close Notepad process with PID $($np.Id)"
    }
}

Write-Host "All done. Logs closed."
