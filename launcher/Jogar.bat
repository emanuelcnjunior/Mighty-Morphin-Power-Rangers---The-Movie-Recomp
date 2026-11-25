@echo off
cd /d "%~dp0"
if exist "%~dp0Launcher.exe" (
    start "" "%~dp0Launcher.exe" %*
) else (
    start "" "%~dp0MightyMorphinPowerRangersTheMovieSNESRecomp.exe" %*
)
