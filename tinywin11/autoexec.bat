@echo off

cd /d %~dp0

REM Register font "Segoe UI"
fontreg.exe

REM Associate .txt and .ini with Notepad
REG ADD "HKCR\.ini" /ve /t REG_SZ /d "txtfile" /f >nul 2>&1
REG ADD "HKCR\.txt" /ve /t REG_SZ /d "txtfile" /f >nul 2>&1
REG ADD "HKCR\txtfile\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\notepad.exe"" %%1" /f >nul 2>&1

REG ADD "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d "0" /f >nul 2>&1

REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v "Desktop" /t REG_EXPAND_SZ /d "%%USERPROFILE%%\Desktop" /f >nul 2>&1

REM Show file extensions on desktop
REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "HideFileExt" /t REG_DWORD /d 0 /f >nul 2>&1

REM Activate Recycle Bin for this USB drive
REG ADD "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "RecycleBinDrives" /t REG_DWORD /d 4294967295 /f >nul 2>&1

REM Associate folders with Explorer++
REG ADD "HKCR\folder\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\Explorer++\Explorer++.exe"" %%1" /f >nul 2>&1

REG DELETE "HKCR\folder\shell\cmd" /f >nul 2>&1
REG ADD "HKCR\folder\shell\cmd" /ve /t REG_SZ /d "CMD" /f >nul 2>&1
REG ADD "HKCR\folder\shell\cmd" /v "Icon" /t REG_SZ /d "cmd.exe" /f >nul 2>&1
REG ADD "HKCR\folder\shell\cmd\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\System32\cmd.exe"" /s /k pushd ""%%V""" /f >nul 2>&1

REG DELETE "HKCR\Directory\shell\cmd" /f >nul 2>&1
REG ADD "HKCR\Directory\shell\cmd" /ve /t REG_SZ /d "CMD" /f >nul 2>&1
REG ADD "HKCR\Directory\shell\cmd" /v "Icon" /t REG_SZ /d "cmd.exe" /f >nul 2>&1
REG ADD "HKCR\Directory\shell\cmd\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\System32\cmd.exe"" /s /k pushd ""%%V""" /f >nul 2>&1

REG DELETE "HKCR\Directory\background\shell" /f >nul 2>&1

REG ADD "HKCR\Directory\background\shell\cmd" /ve /t REG_SZ /d "CMD" /f >nul 2>&1
REG ADD "HKCR\Directory\background\shell\cmd" /v "Icon" /t REG_SZ /d "cmd.exe" /f >nul 2>&1
REG ADD "HKCR\Directory\background\shell\cmd\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\System32\cmd.exe"" /s /k pushd ""%%V""" /f >nul 2>&1

REG DELETE "HKCR\Directory\background\shellex\ContextMenuHandlers\Sharing" /f >nul 2>&1
REG DELETE "HKCR\Directory\shellex\ContextMenuHandlers\Sharing" /f >nul 2>&1

REG DELETE "HKCR\Directory\shell\find" /f >nul 2>&1
REG DELETE "HKCR\folder\shellex" /f >nul 2>&1
REG DELETE "HKCR\.lnk\ShellNew" /f >nul 2>&1

REM Associate common image file types with IrfanView
REG ADD "HKCR\.bmp" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\.gif" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\.jpg" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\.jpeg" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\.png" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\.tif" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\.tiff" /ve /t REG_SZ /d "IrfanView.File" /f >nul 2>&1
REG ADD "HKCR\IrfanView.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\IrfanView\i_view64.exe"" %%1" /f >nul 2>&1

REM Associate .chm and .pdf with WordPad SumatraPDF
REG ADD "HKCR\.epub" /ve /t REG_SZ /d "SumatraPDF.File" /f >nul 2>&1
REG ADD "HKCR\.pdf" /ve /t REG_SZ /d "SumatraPDF.File" /f >nul 2>&1
REG ADD "HKCR\SumatraPDF.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\SumatraPDF\SumatraPDF.exe"" %%1" /f >nul 2>&1
REG ADD "HKCR\chm.file\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\SumatraPDF\SumatraPDF.exe"" %%1" /f >nul 2>&1

REM Associate .rtf with WordPad
REG ADD "HKCR\.rtf" /ve /t REG_SZ /d "rtffile" /f
REG ADD "HKCR\rtffile\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\WordPad\wordpad.exe"" %%1" /f

REM Associate .7z, .iso, .rar and .zip with 7-Zip
REG ADD "HKCR\.7z" /ve /t REG_SZ /d "7zip.File" /f >nul 2>&1
REG ADD "HKCR\.rar" /ve /t REG_SZ /d "7zip.File" /f >nul 2>&1
REG ADD "HKCR\.zip" /ve /t REG_SZ /d "7zip.File" /f >nul 2>&1
REG ADD "HKCR\7zip.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\7-Zip\7zFM.exe"" %%1" /f >nul 2>&1

REM Remove dysfunctional "Open with" shellex
REG DELETE "HKCR\*\shellex\ContextMenuHandlers\Open With" /f >nul 2>&1
REG DELETE "HKCR\*\OpenWithList" /f >nul 2>&1

REM Associate custom OpenWith.exe with all files
REG ADD "HKCR\*\shell\OpenWith" /v "MUIVerb" /t REG_SZ /d "@shell32.dll,-5377" /f >nul 2>&1
REG ADD "HKCR\*\shell\OpenWith\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\OpenWith\OpenWith.exe"" ""%%1""" /f >nul 2>&1

REM Autorun arbitrary programs using the "start" command
REM wpeutil.exe InitializeNetwork /NoWait
REM start "" "%windir%\Notepad.exe"
