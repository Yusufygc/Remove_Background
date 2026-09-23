; Arka Plan Kaldirici AI - Inno Setup kurulum betigi
; PyInstaller ile derlenmis dist/ArkaPlanKaldiriciAI/ klasorunu paketler.
; Once "python main.py" degil, PyInstaller build'i alinmis olmali:
;   pyinstaller --noconfirm --windowed --name "ArkaPlanKaldiriciAI" --icon icons\app_icon.ico
;     --add-data "qml;qml" --add-data "icons;icons"
;     --add-data ".venv\Lib\site-packages\PySide6\qml;PySide6\qml" main.py

#define MyAppName "Arka Plan Kaldirici AI"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Yusuf"
#define MyAppExeName "ArkaPlanKaldiriciAI.exe"

[Setup]
AppId={{B4B6C6C0-6E1D-4F1A-9C4E-2E5F6A1B7C90}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=output
OutputBaseFilename=ArkaPlanKaldiriciAI_Kurulum
SetupIconFile=..\icons\app_icon.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\ArkaPlanKaldiriciAI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
