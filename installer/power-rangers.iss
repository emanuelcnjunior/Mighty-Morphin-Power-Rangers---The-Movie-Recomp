#ifndef StageDir
#error StageDir is required
#endif
#ifndef OutputDir
#define OutputDir "..\dist"
#endif
#ifndef ReleaseVersion
#define ReleaseVersion "0.2.0"
#endif
[Setup]
AppId={{39AAB812-5CF4-4C94-A792-067BEB576404}
AppName=Mighty Morphin Power Rangers - The Movie PC Recomp
AppVersion={#ReleaseVersion}
DefaultDirName={localappdata}\Programs\PowerRangersMovieRecomp
DefaultGroupName=Mighty Morphin Power Rangers - The Movie PC Recomp
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.18362
OutputDir={#OutputDir}
OutputBaseFilename=Power-Rangers-The-Movie-PC-Setup-v{#ReleaseVersion}
Compression=lzma2
SolidCompression=no
WizardStyle=modern
SetupIconFile=assets\power-rangers.ico
UninstallDisplayIcon={app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe
LicenseFile=..\LICENSE
CloseApplications=yes
[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
[Tasks]
Name: "desktopicon"; Description: "Atalho na Área de Trabalho / Desktop shortcut"
[Files]
Source: "{#StageDir}\*"; DestDir: "{app}"; Excludes: "*.sfc,*.smc,*.rom,*.bin,rom.cfg,config.ini,keybinds.ini,state.toml"; Flags: ignoreversion recursesubdirs createallsubdirs
[Messages]
english.WelcomeLabel2=This installer contains no game ROM and performs no downloads. On first launch, select your own original USA ROM of Mighty Morphin Power Rangers - The Movie for SNES.
brazilianportuguese.WelcomeLabel2=Este instalador não contém ROM e não realiza downloads. Na primeira execução, selecione sua ROM americana (USA) original de Mighty Morphin Power Rangers - The Movie para SNES.
[Icons]
Name: "{group}\Mighty Morphin Power Rangers - The Movie"; Filename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconFilename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconIndex: 0; WorkingDir: "{app}"
Name: "{autodesktop}\Mighty Morphin Power Rangers - The Movie"; Filename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconFilename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconIndex: 0; WorkingDir: "{app}"; Tasks: desktopicon
[Run]
Filename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; Description: "Jogar / Play Power Rangers"; Flags: nowait postinstall skipifsilent
; User ROM, saves and configuration are outside {app}; never delete them here.
