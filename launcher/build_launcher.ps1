# Build script for Mighty Morphin Power Rangers: The Movie Launcher
param(
    [string]$Output = "launcher/Launcher.exe"
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$csc = "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe"

if (-not (Test-Path $csc)) {
    throw "C# compiler not found at $csc"
}

Write-Host "Compiling $Output..."
& $csc /nologo /target:winexe /platform:x64 /optimize+ `
    "/win32icon:$PSScriptRoot\power-rangers.ico" `
    "/resource:$PSScriptRoot\logo.png,logo.png" `
    "/out:$Output" "$PSScriptRoot\Launcher.cs"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Launcher build successful: $Output"
} else {
    throw "Launcher build failed with code $LASTEXITCODE"
}
