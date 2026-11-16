[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Rom)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$version = (Get-Content (Join-Path $root 'VERSION') -Raw).Trim()
$setup = Join-Path $root "dist/Power-Rangers-The-Movie-PC-Setup-v$version.exe"
$testRoot = Join-Path $root ('build-installer/install-test-' + [guid]::NewGuid().ToString('N'))
$install = [IO.Path]::GetFullPath((Join-Path $testRoot 'program'))
$data = Join-Path $testRoot 'user-data'
if (!$install.StartsWith(([IO.Path]::GetFullPath($root) + '\'), [StringComparison]::OrdinalIgnoreCase)) {
 throw 'Test install directory escaped the workspace.'
}
$groupName = 'Mighty Morphin Power Rangers - The Movie PC Recomp'
$shortcutName = 'Mighty Morphin Power Rangers - The Movie.lnk'
$group = Join-Path ([Environment]::GetFolderPath('Programs')) $groupName
$desktopShortcut = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) $shortcutName
$startShortcut = Join-Path $group $shortcutName
$registry = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\{39AAB812-5CF4-4C94-A792-067BEB576404}_is1'
if ((Test-Path $group) -or (Test-Path $desktopShortcut) -or (Test-Path $registry)) {
 throw 'Existing installation or shortcuts detected. They will not be overwritten by this test.'
}
$Rom = (Resolve-Path -LiteralPath $Rom).Path
$sha = (Get-FileHash -LiteralPath $Rom -Algorithm SHA256).Hash
$canonicalName = 'Mighty Morphin Power Rangers - The Movie (USA).sfc'
New-Item -ItemType Directory -Force $testRoot | Out-Null
$savedDataRoot = $env:POWER_RANGERS_USER_DATA
$env:POWER_RANGERS_USER_DATA = $data
$results = @()
function Note([string]$message) {
 Write-Output "PASS: $message"
 $script:results += [pscustomobject]@{test=$message; result='PASS'}
}
function Install([string]$name) {
 $arguments = @('/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/SP-',
  '/TASKS=desktopicon', ('/DIR="' + $install + '"'),
  ('/LOG="' + (Join-Path $testRoot ($name + '.log')) + '"'))
 $process = Start-Process -FilePath $setup -ArgumentList $arguments -WindowStyle Hidden -Wait -PassThru
 if ($process.ExitCode -ne 0) { throw "Installer failed: $($process.ExitCode)" }
}
function Uninstall {
 $uninstaller = Join-Path $install 'unins000.exe'
 if (!(Test-Path -LiteralPath $uninstaller)) { return }
 if (!$uninstaller.StartsWith($testRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
  throw 'Refusing to uninstall outside the isolated test directory.'
 }
 $process = Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART' -WindowStyle Hidden -Wait -PassThru
 if ($process.ExitCode -ne 0) { throw "Uninstaller failed: $($process.ExitCode)" }
}
function Smoke([string]$name) {
 $scriptPath = Join-Path $testRoot 'smoke.script'
 "wait 120`nquit`n" | Set-Content -LiteralPath $scriptPath -Encoding ASCII
 $stdout = Join-Path $testRoot ($name + '.stdout.log')
 $stderr = Join-Path $testRoot ($name + '.stderr.log')
 $exe = Join-Path $install 'MightyMorphinPowerRangersTheMovieSNESRecomp.exe'
 $process = Start-Process -FilePath $exe -ArgumentList @('--no-launcher','--script',('"'+$scriptPath+'"')) -WindowStyle Hidden -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
 $null = $process.Handle # Retain the handle so Windows PowerShell can read the exit code.
 if (!$process.WaitForExit(30000)) {
  $process.Kill()
  throw 'Isolated test game did not exit after its scripted run.'
 }
 $process.Refresh()
 if ($process.ExitCode -ne 0) { throw "Installed game failed: $($process.ExitCode)" }
 $log = Get-Content -LiteralPath $stderr -Raw
 if ($log -notmatch 'fullscreen=1' -or $log -notmatch 'first frame simulated' -or
     $log -notmatch 'first audio callback' -or $log -notmatch 'script quit') {
  throw 'Installed runtime did not complete the video/audio/fullscreen smoke test.'
 }
}
try {
 Install 'install'
 $exe = Join-Path $install 'MightyMorphinPowerRangersTheMovieSNESRecomp.exe'
 $romDest = Join-Path $data $canonicalName
 $invalid = Join-Path $testRoot 'invalid.sfc'
 'not a ROM' | Set-Content -LiteralPath $invalid -Encoding ASCII
 $process = Start-Process -FilePath $exe -ArgumentList @('--import-rom',('"'+$invalid+'"')) -WindowStyle Hidden -Wait -PassThru
 if ($process.ExitCode -ne 2 -or (Test-Path $romDest)) { throw 'Import accepted an invalid ROM.' }
 Note 'Installed importer rejects an invalid ROM without writing user data'
 $process = Start-Process -FilePath $exe -ArgumentList @('--import-rom',('"'+$Rom+'"')) -WindowStyle Hidden -Wait -PassThru
 if ($process.ExitCode -ne 0) { throw "Valid ROM import failed: $($process.ExitCode)" }
 if ((Get-FileHash -LiteralPath $romDest -Algorithm SHA256).Hash -ne $sha) { throw 'Imported ROM differs.' }
 Note 'Valid user ROM imported under the canonical name outside the program directory'
 $forbidden = Get-ChildItem -LiteralPath $install -Recurse -File | Where-Object {
  $_.Extension -in @('.sfc','.smc','.rom','.bin','.state','.sav','.srm') -or $_.Name -eq 'rom.cfg'
 }
 if ($forbidden) { throw 'Forbidden game data/cache in installed program payload.' }
 foreach ($dll in @('msvcp140.dll','vcruntime140.dll','vcruntime140_1.dll')) {
  if (!(Test-Path (Join-Path $install $dll))) { throw "Missing runtime DLL: $dll" }
 }
 Note 'Installed payload excludes ROM/cache/saves and includes the Visual C++ runtime'
 $shell = New-Object -ComObject WScript.Shell
 foreach ($path in @($desktopShortcut,$startShortcut)) {
  if (!(Test-Path -LiteralPath $path)) { throw "Missing shortcut: $path" }
  $shortcut = $shell.CreateShortcut($path)
  if ($shortcut.TargetPath -ne $exe -or !$shortcut.IconLocation.StartsWith($exe, [StringComparison]::OrdinalIgnoreCase)) {
   throw 'Shortcut target/icon does not reference the game executable.'
  }
 }
 Add-Type -AssemblyName System.Drawing
 $icon = [Drawing.Icon]::ExtractAssociatedIcon($exe)
 if (!$icon) { throw 'Embedded game icon missing.' }
 $bitmap = $icon.ToBitmap()
 $bitmap.Save((Join-Path $testRoot 'installed-icon.png'), [Drawing.Imaging.ImageFormat]::Png)
 $bitmap.Dispose(); $icon.Dispose()
 Note 'Desktop and Start menu shortcuts use the embedded Red Ranger icon'
 Smoke 'first-run'
 Note 'Installed game starts fullscreen with video/audio using the imported ROM'
 $settings = Join-Path $data 'config.ini'
 $text = (Get-Content -LiteralPath $settings -Raw) -replace '(?m)^Volume\s*=\s*100\s*$', 'Volume = 37'
 Set-Content -LiteralPath $settings -Value $text -Encoding UTF8
 $marker = Join-Path $data 'saves/install-preservation-marker.txt'
 'retain saves' | Set-Content -LiteralPath $marker -Encoding ASCII
 Uninstall
 if ((Test-Path $exe) -or (Test-Path $desktopShortcut) -or (Test-Path $startShortcut)) { throw 'Uninstaller left program or shortcuts.' }
 if (!(Test-Path $marker) -or (Get-FileHash -LiteralPath $romDest).Hash -ne $sha) { throw 'Uninstaller changed user data.' }
 Note 'Uninstall removes the program/shortcuts and preserves the user ROM and save directory'
 Install 'reinstall'
 if ((Get-Content -LiteralPath $settings -Raw) -notmatch 'Volume = 37' -or !(Test-Path $marker)) { throw 'Reinstall overwrote preferences or saves.' }
 Smoke 'after-reinstall'
 Note 'Reinstall preserves configuration/saves and starts using the cached ROM'
 Uninstall
 $results | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $testRoot 'results.json') -Encoding UTF8
 Write-Output "Evidence: $testRoot"
} finally {
 if (Test-Path (Join-Path $install 'unins000.exe')) { Uninstall }
 $env:POWER_RANGERS_USER_DATA = $savedDataRoot
}
