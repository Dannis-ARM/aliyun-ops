# PowerShell script to create a shortcut for the Go program in the user's Startup folder

# Define variables
$GoProgramPath = Join-Path $PSScriptRoot "dist\sg-whitelist-automation.exe" # Assuming the compiled Go executable is in the 'dist' subdirectory
$StartupFolder = [Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupFolder "sg-whitelist-automation.lnk"

# Check if the Go executable exists
if (-not (Test-Path $GoProgramPath)) {
    Write-Host "Error: Go executable not found at $GoProgramPath. Please compile the Go program first."
    Exit 1
}

Write-Host "Creating shortcut in Startup folder..."

# Create WScript.Shell COM object
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $GoProgramPath
$Shortcut.WorkingDirectory = Split-Path $GoProgramPath
$Shortcut.WindowStyle = 1
$Shortcut.Description = "Automatically updates Alibaba Cloud Security Group with current public IP."
$Shortcut.Save()

Write-Host "Shortcut created at $ShortcutPath. The program will run automatically when you log in."
