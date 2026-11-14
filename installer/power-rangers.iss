#ifndef StageDir
#error StageDir is required
#endif
#ifndef OutputDir
#define OutputDir "..\dist"
#endif
#ifndef ReleaseVersion
#define ReleaseVersion "0.2.0"
#endif
#ifndef RomSHA256
#error RomSHA256 is required (from rom_identity.txt)
#endif
#ifndef RomFileName
#error RomFileName is required (from rom_identity.txt)
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
SolidCompression=yes
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
english.WelcomeLabel2=This installer does not include a game ROM. During installation, select your own original USA ROM of Mighty Morphin Power Rangers - The Movie for SNES.
brazilianportuguese.WelcomeLabel2=Este instalador não inclui a ROM do jogo. Durante a instalação, selecione sua própria ROM americana (USA) original de Mighty Morphin Power Rangers - The Movie para SNES.
[Icons]
Name: "{group}\Mighty Morphin Power Rangers - The Movie"; Filename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconFilename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconIndex: 0; WorkingDir: "{app}"
Name: "{autodesktop}\Mighty Morphin Power Rangers - The Movie"; Filename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconFilename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; IconIndex: 0; WorkingDir: "{app}"; Tasks: desktopicon
[Run]
Filename: "{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe"; Description: "Jogar / Play Power Rangers"; Flags: nowait postinstall skipifsilent
; User ROM, saves and configuration are outside {app}; never delete them here.

[Code]
var
  RomPage: TInputFileWizardPage;
  SelectedRom: String;

function ValidRom(const Path: String): Boolean;
begin
  Result := False;
  if not FileExists(Path) then Exit;
  try
    Result := CompareText(GetSHA256OfFile(Path), '{#RomSHA256}') = 0;
  except
    Result := False;
  end;
end;

function InitializeSetup: Boolean;
begin
  Result := True;
  if WizardSilent then begin
    Result := ValidRom(ExpandConstant('{param:ROM|}'));
    if not Result then Log('Valid USA ROM required: supply /ROM="C:\path\game.sfc"');
  end;
end;

procedure InitializeWizard;
var
  ExistingRom, DataDir: String;
begin
  RomPage := CreateInputFilePage(wpSelectDir,
    'ROM americana / USA ROM',
    'Selecione sua ROM original / Select your original ROM',
    'Forneça sua própria ROM USA de Mighty Morphin Power Rangers - The Movie para SNES, sem cabeçalho ou patches. A ROM não acompanha este instalador.' + #13#10#13#10 +
    'Supply your own original USA SNES ROM, without a copier header or patches. This installer does not include a ROM.');
  RomPage.Add('ROM USA (*.sfc; *.smc):', 'SNES ROM (*.sfc;*.smc)|*.sfc;*.smc|Todos os arquivos / All files|*.*', '.sfc');
  RomPage.Values[0] := ExpandConstant('{param:ROM|}');
  if RomPage.Values[0] = '' then begin
    DataDir := GetEnv('POWER_RANGERS_USER_DATA');
    if DataDir = '' then DataDir := ExpandConstant('{localappdata}\PowerRangersMovieRecomp');
    ExistingRom := AddBackslash(DataDir) + '{#RomFileName}';
    if ValidRom(ExistingRom) then RomPage.Values[0] := ExistingRom;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = RomPage.ID then begin
    Result := ValidRom(RomPage.Values[0]);
    if not Result then
      MsgBox('Selecione sua ROM USA original, sem cabeçalho ou patches.' + #13#10 +
        'Select the original USA ROM, without a copier header or patches.', mbError, MB_OK);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  SelectedRom := RomPage.Values[0];
  Result := '';
  if not ValidRom(SelectedRom) then
    Result := 'ROM USA válida obrigatória / A valid original USA ROM is required.';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ExitCode: Integer;
begin
  if CurStep = ssPostInstall then begin
    if not Exec(ExpandConstant('{app}\MightyMorphinPowerRangersTheMovieSNESRecomp.exe'),
      '--import-rom "' + SelectedRom + '"', '', SW_HIDE, ewWaitUntilTerminated, ExitCode) then
      RaiseException('Não foi possível importar a ROM. / Could not import the ROM.');
    if ExitCode <> 0 then
      RaiseException('Falha ao validar ou salvar a ROM. / Failed to validate or save the ROM.');
  end;
end;
