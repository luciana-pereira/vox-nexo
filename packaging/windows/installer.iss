#define AppName "VoxNexo"
#define AppVersion "1.0.0"
#define AppPublisher "VoxNexo"
#define AppExeName "VoxNexo.exe"
#define ProjectRoot GetEnv("PROJECT_ROOT")

[Setup]
AppId={{B7A164EA-2A8D-4F62-A1F6-A11B7A9C88D0}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\VoxNexo
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#ProjectRoot}\dist\installer
OutputBaseFilename=Setup_VoxNexo
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na área de trabalho"; GroupDescription: "Atalhos:"; Flags: unchecked

[Files]
Source: "{#ProjectRoot}\dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Abrir {#AppName}"; Flags: postinstall nowait skipifsilent
