#ifndef MyAppVersion
#define MyAppVersion "0.2.8"
#endif

#ifndef MyOutputBaseFilename
#define MyOutputBaseFilename "JingweiZhizao-Setup-0.2.8"
#endif

[Setup]
AppId={{DEDFB1E7-B5C6-48DD-A042-8C2A855AFE8E}
AppName=经纬智造
AppVersion={#MyAppVersion}
AppVerName=经纬智造 {#MyAppVersion}
AppPublisher=akbar747
AppPublisherURL=https://github.com/akbar747/jingwei-zhizao
AppSupportURL=https://github.com/akbar747/jingwei-zhizao/issues
AppUpdatesURL=https://github.com/akbar747/jingwei-zhizao/releases
DefaultDirName={code:GetDefaultDirName}
DefaultGroupName=经纬智造
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\..\release
OutputBaseFilename={#MyOutputBaseFilename}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\JingweiZhizao.exe
SetupLogging=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务："; Flags: unchecked

[Files]
Source: "..\..\dist\JingweiZhizao\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\经纬智造"; Filename: "{app}\JingweiZhizao.exe"
Name: "{autodesktop}\经纬智造"; Filename: "{app}\JingweiZhizao.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\JingweiZhizao.exe"; Description: "启动经纬智造"; Flags: nowait postinstall skipifsilent
[Code]
function GetDefaultDirName(Param: string): string;
var
  BaseDir: string;
begin
  BaseDir := GetEnv('LOCALAPPDATA');
  if BaseDir = '' then
    BaseDir := ExpandConstant('{userappdata}');
  Result := BaseDir + '\Programs\JingweiZhizao';
end;