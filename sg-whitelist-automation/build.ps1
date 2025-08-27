# PowerShell script to build the Go program and place it in a 'dist' folder

# Define variables
$ProjectDir = $PSScriptRoot
$DistDir = Join-Path $ProjectDir "dist"
$ExecutableName = "sg-whitelist-automation.exe"
$GoProgramPath = Join-Path $ProjectDir "main.go"
$OutputExecutablePath = Join-Path $DistDir $ExecutableName

Write-Host "Starting build process for Aliyun SG Whitelist Automation..."

# 1. Create 'dist' directory if it doesn't exist
if (-not (Test-Path $DistDir)) {
    Write-Host "Creating 'dist' directory: $DistDir"
    New-Item -ItemType Directory -Path $DistDir | Out-Null
} else {
    Write-Host "'dist' directory already exists: $DistDir"
}

# 2. Build the Go program
Write-Host "Building Go program from $GoProgramPath to $OutputExecutablePath..."
try {
    Push-Location $ProjectDir
    go build -o $OutputExecutablePath $GoProgramPath
    Pop-Location
    Write-Host "Go program built successfully."
} catch {
    Write-Host "Error building Go program: $($_.Exception.Message)"
    Exit 1
}

Write-Host "Build process completed."
