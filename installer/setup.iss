#define AppName "PhotoCompressorService"
#define AppVersion "1.0.2"
#define ServiceName "PhotoCompressorService"
#define ServiceDisplayName "Photo Compressor Service"
#define Publisher "Internal Tools"

[Setup]
AppId={{B7C3F6B4-2F2C-4A6E-9B1A-6B6C9F0F9B10}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#Publisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=output
OutputBaseFilename={#AppName}-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=admin
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppName}.exe
SetupIconFile=..\assets\icon.ico

[Tasks]
Name: "desktopicon"; Description: "Створити ярлик головної сторінки на робочому столі"; GroupDescription: "Додаткові ярлики:"

[Files]
Source: "..\dist\PhotoCompressorService.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "nssm.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\docs\README.md"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "..\assets\icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Code]
procedure CreateUrlShortcut(FolderPath, FileBaseName, Url, IconPath: String);
var
  Content: String;
begin
  Content := '[InternetShortcut]' + #13#10 +
             'URL=' + Url + #13#10 +
             'IconFile=' + IconPath + #13#10 +
             'IconIndex=0' + #13#10;
  ForceDirectories(FolderPath);
  SaveStringToFile(FolderPath + '\' + FileBaseName + '.url', Content, False);
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  NssmPath: String;
begin
  NssmPath := ExpandConstant('{app}\nssm.exe');
  if FileExists(NssmPath) then
  begin
    Exec(NssmPath, 'stop {#ServiceName}', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    Exec(NssmPath, 'remove {#ServiceName} confirm', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
  Result := '';
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  IconPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    IconPath := ExpandConstant('{app}\icon.ico');
    CreateUrlShortcut(ExpandConstant('{group}'), 'Головна сторінка', 'http://127.0.0.1:8788/', IconPath);
    if WizardIsTaskSelected('desktopicon') then
      CreateUrlShortcut(ExpandConstant('{autodesktop}'), 'PhotoCompressorService', 'http://127.0.0.1:8788/', IconPath);
  end;
end;

[Icons]
Name: "{group}\Логи служби"; Filename: "{commonappdata}\{#AppName}\logs"; IconFilename: "{app}\icon.ico"
Name: "{group}\Конфігурація"; Filename: "{commonappdata}\{#AppName}\config.json"; IconFilename: "{app}\icon.ico"
Name: "{group}\Документація"; Filename: "{app}\docs\README.md"; IconFilename: "{app}\icon.ico"
Name: "{group}\Видалити {#AppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icon.ico"

[UninstallDelete]
Type: files; Name: "{group}\Головна сторінка.url"
Type: files; Name: "{autodesktop}\PhotoCompressorService.url"

[Run]
Filename: "{app}\nssm.exe"; Parameters: "install {#ServiceName} ""{app}\{#AppName}.exe"""; Flags: runhidden; StatusMsg: "Реєстрація служби..."
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} AppDirectory ""{app}"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} DisplayName ""{#ServiceDisplayName}"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} Description ""Стиснення та конвертація фото для 1С (HTTP API на localhost)."""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} Start SERVICE_AUTO_START"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} AppStdout ""{commonappdata}\{#AppName}\logs\stdout.log"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} AppStderr ""{commonappdata}\{#AppName}\logs\stderr.log"""; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} AppRotateFiles 1"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "set {#ServiceName} AppRotateBytes 5242880"; Flags: runhidden
Filename: "{app}\nssm.exe"; Parameters: "start {#ServiceName}"; Flags: runhidden; StatusMsg: "Запуск служби..."
Filename: "http://127.0.0.1:8788/"; Description: "Відкрити головну сторінку зараз"; Flags: postinstall shellexec skipifsilent

[UninstallRun]
Filename: "{app}\nssm.exe"; Parameters: "stop {#ServiceName}"; Flags: runhidden; RunOnceId: "StopService"
Filename: "{app}\nssm.exe"; Parameters: "remove {#ServiceName} confirm"; Flags: runhidden; RunOnceId: "RemoveService"

[Dirs]
Name: "{commonappdata}\{#AppName}"
Name: "{commonappdata}\{#AppName}\logs"
