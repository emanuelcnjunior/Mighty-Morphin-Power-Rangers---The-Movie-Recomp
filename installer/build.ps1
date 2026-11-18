[CmdletBinding()]
param(
 [string]$BuildDir = 'build-installer',
 [string]$CrtDir = '',
 [switch]$SkipBuild
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
$build = [IO.Path]::GetFullPath((Join-Path $root $BuildDir))
$version = (Get-Content (Join-Path $root 'VERSION') -Raw).Trim()
if ($version -notmatch '^\d+\.\d+\.\d+$') { throw 'VERSION must contain a numeric x.y.z version.' }
$identity = @{}
Get-Content (Join-Path $root 'rom_identity.txt') | ForEach-Object {
 if ($_ -match '^\s*([a-z_0-9]+)\s*=\s*([^#]+)') { $identity[$matches[1]] = $matches[2].Trim().Trim('"') }
}
function Invoke-Native([string]$Program, [string[]]$Arguments) {
 $saved = $ErrorActionPreference
 try { $ErrorActionPreference = 'Continue'; & $Program @Arguments; $code = $LASTEXITCODE }
 finally { $ErrorActionPreference = $saved }
 if ($code -ne 0) { throw "$Program failed: $code" }
}
if (!$SkipBuild) {
 $configure = @('-S',$root,'-B',$build,'-G','Visual Studio 17 2022','-A','x64',
   '-DPOWER_RANGERS_RETAIL_WINDOWS=ON','-DPOWER_RANGERS_TEST_ENTRY=',
   '-DSNESRECOMP_SETUP_HOST=OFF')
 $sdlSource = Join-Path $root 'build/_deps/sdl3-src'
 if (Test-Path (Join-Path $sdlSource 'CMakeLists.txt')) { $configure += "-DSNESRECOMP_SDL3_SOURCE_DIR=$($sdlSource.Replace('\','/'))" }
 Invoke-Native cmake $configure
 Invoke-Native cmake @('--build',$build,'--config','Release','--parallel','4')
}
$cache = Get-Content (Join-Path $build 'CMakeCache.txt') -Raw
if ($cache -notmatch 'POWER_RANGERS_RETAIL_WINDOWS:BOOL=ON' -or
    $cache -notmatch 'SNESRECOMP_SETUP_HOST:BOOL=OFF' -or
    $cache -match 'POWER_RANGERS_TEST_ENTRY:STRING=\S+') { throw 'A playable retail build is required.' }
$exe = Join-Path $build 'Release/MightyMorphinPowerRangersTheMovieSNESRecomp.exe'
if (!(Test-Path $exe)) { throw 'Release executable missing.' }
$stage = Join-Path $root ('dist/stage-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force $stage | Out-Null
Copy-Item -LiteralPath $exe -Destination $stage
Copy-Item -LiteralPath (Join-Path $root 'recomplauncher.json') -Destination $stage
Copy-Item installer/LEIA-ME.txt (Join-Path $stage 'LEIA-ME.txt')
$assets = Join-Path (Split-Path $exe) 'assets'
$required = @('fonts/LatoLatin-Regular.ttf','fonts/LatoLatin-Bold.ttf',
 'fonts/NotoSansSymbols2-Regular.ttf','fonts/OpenMoji-black-glyf.ttf',
 'img/brand_mark.tga','img/boxart.tga','img/pad.tga','img/flags.png','img/verdict_ok.tga',
 'img/verdict_bad.tga','img/verdict_none.tga','img/verdict_warn.tga')
foreach ($item in $required) {
 if (!(Test-Path (Join-Path $assets $item))) { throw "Missing launcher resource: $item" }
}
Copy-Item -LiteralPath $assets -Destination (Join-Path $stage 'assets') -Recurse
$packages = Join-Path (Split-Path $exe) 'mods/preloaded/packages'
if (Test-Path $packages) {
 $packageDest = Join-Path $stage 'mods/preloaded'
 New-Item -ItemType Directory -Force $packageDest | Out-Null
 Copy-Item -LiteralPath $packages -Destination $packageDest -Recurse
}
$licenses = Join-Path $stage 'licenses'
New-Item -ItemType Directory $licenses | Out-Null
Copy-Item LICENSE (Join-Path $licenses 'project.txt')
Copy-Item snesrecomp/LICENSE (Join-Path $licenses 'framework.txt')
Copy-Item snesrecomp/THIRD_PARTY_ATTRIBUTION.md $licenses
Copy-Item installer/assets/ICON-SOURCE.md $licenses
$licenseRoots = @((Join-Path $root 'recomp-ui'),
 (Join-Path $root 'build/_deps/sdl3-src'), (Join-Path $build '_deps/sdl3-src')) |
 Where-Object { Test-Path $_ } | Select-Object -Unique
Get-ChildItem $licenseRoots -Recurse -File -Include '*LICENSE*','*COPYING*','*OFL*' | ForEach-Object {
 $name = ($_.FullName.Substring($root.Length+1) -replace '[:\\/]', '_')
 Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $licenses $name)
}
Copy-Item recomp-ui/assets/common/fonts/NOTICE.md (Join-Path $licenses 'fonts-NOTICE.md')
Copy-Item recomp-ui/assets/common/img/NOTICE.md (Join-Path $licenses 'images-NOTICE.md')
if (!$CrtDir) {
 $vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio/Installer/vswhere.exe'
 $visualStudio = & $vswhere -latest -products '*' -property installationPath
 $redist = Join-Path $visualStudio 'VC/Redist/MSVC'
 $CrtDir = Get-ChildItem -LiteralPath $redist -Directory | Where-Object { $_.Name -match '^\d' } |
  Sort-Object Name -Descending | ForEach-Object { Join-Path $_.FullName 'x64/Microsoft.VC143.CRT' } |
  Where-Object { Test-Path $_ } | Select-Object -First 1
}
foreach ($dll in @('msvcp140.dll','vcruntime140.dll','vcruntime140_1.dll')) {
 if (!(Test-Path (Join-Path $CrtDir $dll))) { throw "Missing redistributable: $dll" }
 Copy-Item -LiteralPath (Join-Path $CrtDir $dll) -Destination $stage
}
# dependencies.cmake copies only the signed CRT files the executable actually
# imports (and their transitive dependencies), not every DLL in the redist set.
Invoke-Native cmake @("-DEXE=$(Join-Path $stage (Split-Path $exe -Leaf))",
 "-DCRT=$CrtDir", "-DSTAGE=$stage", '-P', 'installer/dependencies.cmake')
$forbidden = Get-ChildItem $stage -File -Recurse | Where-Object {
 $_.Extension -in @('.sfc','.smc','.rom','.bin','.state','.sav','.srm','.spc','.bps','.ips','.py','.rs','.obj','.pdb') -or
 $_.Name -in @('rom.cfg','config.ini','keybinds.ini','state.toml','CMakeCache.txt') -or
 (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash -eq $identity['expected_sha256']
}
if ($forbidden) { throw 'Forbidden ROM, user data or development file in staging directory.' }
$manifest = Get-ChildItem $stage -File -Recurse | ForEach-Object {
 [ordered]@{ path=$_.FullName.Substring($stage.Length+1); bytes=$_.Length;
  sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
}
$manifest | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $stage 'manifest.json')
$portable = Join-Path $root "dist/Power-Rangers-The-Movie-PC-v$version-Windows-x64.zip"
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $portable -Force
$sum = (Get-FileHash -LiteralPath $portable -Algorithm SHA256).Hash.ToLowerInvariant() +
 '  ' + (Split-Path $portable -Leaf)
$sum | Set-Content -Encoding ASCII ($portable + '.sha256')
$sum | Set-Content -Encoding ASCII (Join-Path $root 'dist/SHA256SUMS.txt')
Write-Output $portable
Write-Output ($portable + '.sha256')
Write-Output (Join-Path $root 'dist/SHA256SUMS.txt')
