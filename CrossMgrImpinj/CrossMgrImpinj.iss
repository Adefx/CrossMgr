; -- CrossMgrImpinj.iss --

[Setup]
AppName=CrossMgrImpinj
#include "Version.py"
DefaultDirName={pf}\CrossMgrImpinj
DefaultGroupName=CrossMgrImpinj
UninstallDisplayIcon={app}\CrossMgrImpinj.exe
Compression=lzma
SolidCompression=yes
SourceDir=dist
OutputDir=..\install
OutputBaseFilename=CrossMgrImpinj_Setup
ChangesAssociations=yes

[Registry]
Root: HKCR; Subkey: "CrossMgrImpinj\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\CrossMgrImpinj.exe,0"
Root: HKCR; Subkey: "CrossMgrImpinj\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\CrossMgrImpinj.exe"" ""%1"""

[Tasks] 
Name: "desktopicon"; Description: "Create a &desktop icon"; 
	
[Files]
Source: "*.*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\CrossMgrImpinj"; Filename: "{app}\CrossMgrImpinj.exe"
Name: "{userdesktop}\CrossMgrImpinj"; Filename: "{app}\CrossMgrImpinj.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\CrossMgrImpinj.exe"; Description: "Launch CrossMgrImpinj"; Flags: nowait postinstall skipifsilent