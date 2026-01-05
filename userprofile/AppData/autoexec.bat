@echo off

cd /d %~dp0

REG ADD "HKCU\Control Panel\Desktop\WindowMetrics" /v MinAnimate /t REG_SZ /d "0" /f >nul 2>&1

REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v "Desktop" /t REG_EXPAND_SZ /d "%%USERPROFILE%%\Desktop" /f

REM Show file extensions on desktop
REG ADD "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "HideFileExt" /t REG_DWORD /d 0 /f

REM Activate Recycle Bin for this USB drive
REG ADD "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "RecycleBinDrives" /t REG_DWORD /d 4294967295 /f

REM Associate folders with Explorer++
REG ADD "HKCR\folder\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\Explorer++\Explorer++.exe"" %%1" /f

REG DELETE "HKCR\folder\shell\cmd" /f
REG ADD "HKCR\folder\shell\cmd" /ve /t REG_SZ /d "CMD" /f
REG ADD "HKCR\folder\shell\cmd" /v "Icon" /t REG_SZ /d "cmd.exe" /f
REG ADD "HKCR\folder\shell\cmd\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\System32\cmd.exe"" /s /k pushd ""%%V""" /f

REG DELETE "HKCR\folder\shell\powershell" /f
REG ADD "HKCR\folder\shell\powershell" /ve /t REG_SZ /d "PowerShell" /f
REG ADD "HKCR\folder\shell\powershell" /v "Icon" /t REG_SZ /d "pwsh.exe" /f
REG ADD "HKCR\folder\shell\powershell\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\PowerShell\pwsh.exe"" -noexit -command Set-Location -literalPath ""%%V""" /f

REG DELETE "HKCR\Directory\shell\cmd" /f
REG ADD "HKCR\Directory\shell\cmd" /ve /t REG_SZ /d "CMD" /f
REG ADD "HKCR\Directory\shell\cmd" /v "Icon" /t REG_SZ /d "cmd.exe" /f
REG ADD "HKCR\Directory\shell\cmd\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\System32\cmd.exe"" /s /k pushd ""%%V""" /f

REG DELETE "HKCR\Directory\shell\powershell" /f
REG ADD "HKCR\Directory\shell\powershell" /ve /t REG_SZ /d "PowerShell" /f
REG ADD "HKCR\Directory\shell\powershell" /v "Icon" /t REG_SZ /d "pwsh.exe" /f
REG ADD "HKCR\Directory\shell\powershell\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\PowerShell\pwsh.exe"" -noexit -command Set-Location -literalPath ""%%V""" /f

REG DELETE "HKCR\Directory\background\shell" /f

REG ADD "HKCR\Directory\background\shell\cmd" /ve /t REG_SZ /d "CMD" /f
REG ADD "HKCR\Directory\background\shell\cmd" /v "Icon" /t REG_SZ /d "cmd.exe" /f
REG ADD "HKCR\Directory\background\shell\cmd\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\System32\cmd.exe"" /s /k pushd ""%%V""" /f

REG ADD "HKCR\Directory\background\shell\powershell" /ve /t REG_SZ /d "PowerShell" /f
REG ADD "HKCR\Directory\background\shell\powershell" /v "Icon" /t REG_SZ /d "pwsh.exe" /f
REG ADD "HKCR\Directory\background\shell\powershell\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\PowerShell\pwsh.exe"" -noexit -command Set-Location -literalPath ""%%V""" /f

REG DELETE "HKCR\Directory\background\shellex\ContextMenuHandlers\Sharing" /f
REG DELETE "HKCR\Directory\shellex\ContextMenuHandlers\Sharing" /f

REG DELETE "HKCR\Directory\shell\find" /f

REG DELETE "HKCR\folder\shellex" /f

REG DELETE "HKCR\.lnk\ShellNew" /f

REM Associate .txt and .ini with Notepad
REG ADD "HKCR\.ini" /ve /t REG_SZ /d "txtfile" /f
REG ADD "HKCR\.txt" /ve /t REG_SZ /d "txtfile" /f
REM REG ADD "HKCR\.txt\ShellNew" /v "NullFile" /t REG_SZ /d "" /f
REG ADD "HKCR\txtfile\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%windir%%\notepad.exe"" %%1" /f

REM Associate .ps1 with PowerShell 7
REG ADD "HKCR\.ps1" /ve /t REG_SZ /d "PowerShell.File" /f
REG ADD "HKCR\PowerShell.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\PowerShell\pwsh.exe"" %%1" /f

REM Associate common image file types with IrfanView
REG ADD "HKCR\.bmp" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\.gif" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\.jpg" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\.jpeg" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\.png" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\.tif" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\.tiff" /ve /t REG_SZ /d "IrfanView.File" /f
REG ADD "HKCR\IrfanView.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\IrfanView\i_view64.exe"" %%1" /f

REM Associate .chm and .pdf with WordPad SumatraPDF
REM REG ADD "HKCR\.chm" /ve /t REG_SZ /d "SumatraPDF.File" /f
REG ADD "HKCR\.epub" /ve /t REG_SZ /d "SumatraPDF.File" /f
REG ADD "HKCR\.pdf" /ve /t REG_SZ /d "SumatraPDF.File" /f
REG ADD "HKCR\SumatraPDF.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\SumatraPDF\SumatraPDF.exe"" %%1" /f
REG ADD "HKCR\chm.file\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\SumatraPDF\SumatraPDF.exe"" %%1" /f

REM Associate .rtf with WordPad
REG ADD "HKCR\.rtf" /ve /t REG_SZ /d "rtffile" /f
REG ADD "HKCR\rtffile\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\WordPad\wordpad.exe"" %%1" /f

REM Associate .7z, .iso, .rar and .zip with 7-Zip
REG ADD "HKCR\.7z" /ve /t REG_SZ /d "7zip.File" /f
::REG ADD "HKCR\.iso" /ve /t REG_SZ /d "7zip.File" /f
REG ADD "HKCR\.rar" /ve /t REG_SZ /d "7zip.File" /f
REG ADD "HKCR\.zip" /ve /t REG_SZ /d "7zip.File" /f
REG ADD "HKCR\7zip.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\7-Zip\7zFM.exe"" %%1" /f

REM Associate .iso, .vhd and .vhdx with VhdManager
REG DELETE "HKCR\Windows.IsoFile" /f
REG DELETE "HKCR\Windows.VhdFile" /f
REG DELETE "HKCR\.iso\OpenWithProgids" /f
REG ADD "HKCR\.iso" /ve /t REG_SZ /d "VhdManager.File" /f
REG ADD "HKCR\.vhd" /ve /t REG_SZ /d "VhdManager.File" /f
REG ADD "HKCR\.vhdx" /ve /t REG_SZ /d "VhdManager.File" /f
REG ADD "HKCR\VhdManager.File\shell" /ve /t REG_SZ /d "Mount" /f
REG ADD "HKCR\VhdManager.File\shell\Mount\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\VhdManager\VhdManager_x64.exe"" /A %%1" /f
REG ADD "HKCR\VhdManager.File\shell\Unmount\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\VhdManager\VhdManager_x64.exe"" /D %%1" /f

REM Associate .py and .pyw files with Python
REG ADD "HKCR\.py" /ve /t REG_SZ /d "Python.File" /f
REG ADD "HKCR\Python.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\Python\python.exe"" %%1" /f
REG ADD "HKCR\.pyw" /ve /t REG_SZ /d "PythonW.File" /f
REG ADD "HKCR\PythonW.File\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\Python\pythonw.exe"" %%1" /f

REM Associate .txt and .ini with Notepad
REG ADD "HKCR\.ttf" /ve /t REG_SZ /d "ttffile" /f
REG ADD "HKCR\.ttc" /ve /t REG_SZ /d "ttffile" /f
REG ADD "HKCR\ttffile\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\Windows\fontview.exe"" %%1" /f

REM Remove dysfunctional "Open with" shellex
REG DELETE "HKCR\*\shellex\ContextMenuHandlers\Open With" /f
REG DELETE "HKCR\*\OpenWithList" /f

REM Associate custom OpenWith.exe with all files
REG ADD "HKCR\*\shell\OpenWith" /ve /t REG_SZ /d "Open with..." /f
REG ADD "HKCR\*\shell\OpenWith\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\OpenWith\OpenWith.exe"" ""%%1""" /f

REM Associate .dll with PEView
REG ADD "HKCR\dllfile\shell\open\command" /ve /t REG_EXPAND_SZ /d """%%programs%%\PEView\peview.exe"" ""%%1""" /f

REM Autorun arbitrary programs using the "start" command
REM start "" "%windir%\Notepad.exe"
REM start "" "%programs%\PENetwork\PENetwork.exe"
