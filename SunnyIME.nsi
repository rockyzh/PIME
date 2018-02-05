; SunnyIME.nsi
;

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------
;Include Modern UI

  !include "MUI2.nsh"

;--------------------------------

; The name of the installer
Name "SunnyIME"

!define PRODUCT_NAME "阳光藏文输入法"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER ""

!define MUI_ICON "SunnyIME\python\input_methods\tibetan\icon.ico"
;!define MUI_HEADERIMAGE
;!define MUI_HEADERIMAGE_BITMAP "path\to\InstallerLogo.bmp"
;!define MUI_HEADERIMAGE_RIGHT

; The file to write
OutFile SunnyIMEInstaller.exe

; The default installation directory
InstallDir $PROGRAMFILES\PIME

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\SunnyIME" "Install_Dir"

;--------------------------------
!include LogicLib.nsh

Function .onInit
UserInfo::GetAccountType
pop $0
${If} $0 != "admin" ;Require admin rights on NT4+
    MessageBox mb_iconstop "Administrator rights required!"
    SetErrorLevel 740 ;ERROR_ELEVATION_REQUIRED
    Quit
${EndIf}
FunctionEnd

;--------------------------------
;Interface Settings

  !define MUI_ABORTWARNING

;--------------------------------
;Pages

  ;!insertmacro MUI_PAGE_LICENSE "${NSISDIR}\Docs\SunnyIME\License.txt"
  !insertmacro MUI_PAGE_COMPONENTS
  ;!insertmacro MUI_PAGE_DIRECTORY
  !insertmacro MUI_PAGE_INSTFILES
  
  !insertmacro MUI_UNPAGE_CONFIRM
  !insertmacro MUI_UNPAGE_INSTFILES
  
;--------------------------------
;Languages
 
  !insertmacro MUI_LANGUAGE "SimpChinese"

;--------------------------------

; The stuff to install
Section "SunnyIME (required)"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File /r SunnyIME\*.*
  File "SunnyIME.nsi"

  ExecWait 'regsvr32 /s "$INSTDIR\x64\PIMETextService.dll"'
  ExecWait 'regsvr32 /s "$INSTDIR\x86\PIMETextService.dll"'

  ;RegDLL "$INSTDIR\x64\PIMETextService.dll"
  ;RegDLL "$INSTDIR\x86\PIMETextService.dll"

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\SunnyIME "Install_Dir" "$INSTDIR"
  
  WriteRegStr HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "PIMELauncher" "$INSTDIR\PIMELauncher.exe"
  Exec '"$INSTDIR\PIMELauncher.exe"'

  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SunnyIME" "DisplayName" "阳光藏文输入法"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SunnyIME" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SunnyIME" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SunnyIME" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
SectionEnd

;--------------------------------
;Uninstaller Section

Section "Uninstall"

  ;ADD YOUR OWN FILES HERE...

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\SunnyIME"
  DeleteRegKey HKLM SOFTWARE\SunnyIME

  DeleteRegValue HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Run" "PIMELauncher"

  ExecWait 'regsvr32 /u /s "$INSTDIR\x64\PIMETextService.dll"'
  ExecWait 'regsvr32 /u /s "$INSTDIR\x86\PIMETextService.dll"'

  ;UnRegDLL "$INSTDIR\x64\PIMETextService.dll"
  ;UnRegDLL "$INSTDIR\x86\PIMETextService.dll"

  ; Remove files and uninstaller
  Delete $INSTDIR\SunnyIME.nsi
  Delete $INSTDIR\uninstall.exe

  ; Remove directories used
  RMDir /r "$INSTDIR"

  DeleteRegKey /ifempty HKCU "Software\SunnyIME"

SectionEnd