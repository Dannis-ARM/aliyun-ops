# PowerShell script to register the Go program as a scheduled task

# Define variables
$TaskName = "AliyunSGWhitelist"
$Description = "Automatically updates Alibaba Cloud Security Group with current public IP."
$GoProgramPath = Join-Path $PSScriptRoot "dist\sg-whitelist-automation.exe" # Assuming the compiled Go executable is in the 'dist' subdirectory
$LogFilePath = Join-Path $PSScriptRoot "sg-whitelist-automation.log"

# Check if the Go executable exists
if (-not (Test-Path $GoProgramPath)) {
    Write-Host "Error: Go executable not found at $GoProgramPath. Please compile the Go program first."
    Exit 1
}

# Create a scheduled task
Write-Host "Creating scheduled task '$TaskName'..."

# Action: Run the Go program
$Action = New-ScheduledTaskAction `
    -Execute $GoProgramPath `
    -Argument "> `"$LogFilePath`" 2>&1"

# Trigger: On system startup
$Trigger = New-ScheduledTaskTrigger `
    -AtStartup

# Settings: Run with highest privileges, allow to run on demand, stop if longer than 1 hour
$Settings = New-ScheduledTaskSettingsSet `
    -RunLevel Highest `
    -AllowStartOnDemand `
    -StopIfGoingOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Principal: Run as SYSTEM user
$Principal = New-ScheduledTaskPrincipal `
    -UserID "SYSTEM" `
    -LogonType ServiceAccount

# Register the scheduled task (split into multiple lines for readability)
Register-ScheduledTask `
    -TaskName $TaskName `
    -Description $Description `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Force

if ($LASTEXITCODE -eq 0) {
    Write-Host "Scheduled task '$TaskName' created successfully."
    Write-Host "The program will run on system startup and log output to $LogFilePath."
}
else {
    Write-Host "Error creating scheduled task '$TaskName'. Exit code: $LASTEXITCODE"
}

# Optional: Run the task immediately for testing
# Start-ScheduledTask -TaskName $TaskName
