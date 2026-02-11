@echo off
setlocal
set EXITCODE=0

REM Make sure the user has administrator privileges
set ADMINTESTDIR=%WINDIR%\System32\Test_%RANDOM%
mkdir "%ADMINTESTDIR%" 2>NUL
if errorlevel 1 (
	echo ERROR: You need to run this command with administrator privileges.
  	goto fail
) else (
	rd /s /q "%ADMINTESTDIR%"
)

REM ################################################
REM Config
REM ################################################

if exist "C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\" (
	REM When ADK is in the default installation directory
	set "ADK_DIR=C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit"
) else (
	REM When ADK is in a custom diretory (as in my case)
	if exist "D:\dev\adk\10.1.26100.2454\" (
		set "ADK_DIR=D:\dev\adk\10.1.26100.2454"
	) else (
		echo ERROR: ADK not found.
  		goto fail
	)
)

REM 4 GiB
set IMG_SIZE=4294967296

set BASENAME=TinyWin11_English

REM ################################################
REM /Config
REM ################################################

REM Find unused drive letter
for %%a in (Z Y X W V U T S R Q P O N M L K J I H G F E D C) do if not exist %%a:\\ set DRIVE_LETTER=%%a
if "%DRIVE_LETTER%" == "" (
	echo ERROR: Failed to find an unused drive letter.
	goto :eof
)

cd /d %~dp0
set "CWD=%CD%"
set PATH=%CD%\tools;%PATH%

set "TARGET_DIR=%CWD%"
set "WINPE_DIR=%CWD%\WinPE"
set "IMG_FILE=%TARGET_DIR%\%BASENAME%.img"
set "VHD_FILE=%TARGET_DIR%\%BASENAME%.vhd"
set "VMDK_FILE=%TARGET_DIR%\vmware\%BASENAME%.vmdk"

call "%ADK_DIR%\Deployment Tools\DandISetEnv.bat"

REM DandISetEnv.bat has the bad habit to change the CWD, revert this
cd /d "%CWD%"

REM Clean up old stuff
if exist "%IMG_FILE%" (
	del /f "%IMG_FILE%" 2>nul
)
if errorlevel 1 (
  echo ERROR: Failed to delete "%IMG_FILE%".
  goto fail
)

if exist "%VHD_FILE%" (
	del /f "%VHD_FILE%" 2>nul
)
if errorlevel 1 (
  echo ERROR: Failed to delete "%VHD_FILE%".
  goto fail
)

if exist "%VMDK_FILE%" (
	del /f "%VMDK_FILE%" 2>nul
)
if errorlevel 1 (
  echo ERROR: Failed to delete "%VMDK_FILE%".
  goto fail
)

if exist "%WINPE_DIR%\" (
	rmdir /s /q "%WINPE_DIR%" 2>nul
)
if errorlevel 1 (
  echo ERROR: Failed to remove "%WINPE_DIR%".
  goto fail
)

echo.
echo ====================================
echo Creating raw image file...
echo ====================================
fsutil file createnew "%IMG_FILE%" %IMG_SIZE%
if errorlevel 1 (
  echo ERROR: Failed to create "%IMG_FILE%".
  goto fail
)

echo.
echo ====================================
echo Converting image file to VHD...
echo ====================================
ren "%IMG_FILE%" %BASENAME%.vhd
vhdtool /convert "%VHD_FILE%"
if errorlevel 1 (
  echo ERROR: Failed to append VHD footer.
  goto fail
)

echo.
echo ====================================
echo Mounting VHD disk image...
echo ====================================
(echo select vdisk file="%VHD_FILE%" & echo attach vdisk & echo create partition primary & echo select partition 1 & echo format fs=ntfs quick & echo assign letter=%DRIVE_LETTER% & echo exit) | diskpart
if errorlevel 1 (
  echo ERROR: Failed to mount "%VHD_FILE%".
  goto fail
)

echo.
echo ====================================
echo Creating WinPE dir...
echo ====================================
call copype amd64 "%WINPE_DIR%" >nul
if errorlevel 1 (
  echo ERROR: copype.cmd failed.
  goto fail
)
cd /d "%CWD%"

echo.
echo ====================================
echo Updating WinPE dir...
echo ====================================
@for /f %%a in ('dir /b "%WINPE_DIR%\media\*-*"') do @rmdir /q /s "%WINPE_DIR%\media\%%a"

echo.
echo ====================================
echo Updating boot.wim...
echo ====================================

dism /mount-wim /mountdir:"%WINPE_DIR%\mount" /wimfile:"%WINPE_DIR%\media\sources\boot.wim" /index:1

REM Add PowerShell
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\WinPE-WMI.cab"
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\en-us\WinPE-WMI_en-us.cab"

dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\WinPE-NetFx.cab"
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\en-us\WinPE-NetFX_en-us.cab"

dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\WinPE-Scripting.cab"
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\en-us\WinPE-Scripting_en-us.cab"

dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\WinPE-PowerShell.cab"
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\en-us\WinPE-PowerShell_en-us.cab"

dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\WinPE-StorageWMI.cab"
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\en-us\WinPE-StorageWMI_en-us.cab"

dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\WinPE-DismCmdlets.cab"
dism /image:"%WINPE_DIR%\mount" /Add-Package /PackagePath:"%WinPERoot%\amd64\WinPE_OCs\en-us\WinPE-DismCmdlets_en-us.cab"

REM Copy fonts to Windows\fonts\
REM (This will cause some "access denied" error for fonts (owned by TrustedInstaller) that already exist, but they don't matter)
xcopy /q /y /c userprofile\fonts\* "%WINPE_DIR%\mount\Windows\Fonts\" 2>nul

REM Copy some stuff to Windows\System32
xcopy /q /y /c /e tinywin11\system32\* "%WINPE_DIR%\mount\Windows\System32\"

dism /unmount-wim /mountdir:"%WINPE_DIR%\mount" /commit

REM Clean up the boot.wim (purge deleted stuff)
dism /export-image /sourceimagefile:"%WINPE_DIR%\media\sources\boot.wim" /SourceIndex:1 /destinationimagefile:"%WINPE_DIR%\media\sources\boot_cleaned.wim"
del /f "%WINPE_DIR%\media\sources\boot.wim"
ren "%WINPE_DIR%\media\sources\boot_cleaned.wim" boot.wim

echo.
echo ====================================
echo Write WinPE to mounted VHD disk image...
echo ====================================

REM The following lines are extracted from ADK's MakeWinPEMedia.cmd.
REM We can't run MakeWinPEMedia.cmd because it insists to format the
REM drive with FAT32, but our (virtual) drive is already formatted
REM with NTFS, and we need NTFS to make the drive's recycle bin and
REM watching for changes of the dektop directory work.

set DEST=%DRIVE_LETTER%:
set BOOTMGRPATH=%WINPE_DIR%\bootbins\bootmgfw.efi

if exist "%WINPE_DIR%\media\EFI\BOOT\bootx64.efi" (
  copy "%BOOTMGRPATH%" "%WINPE_DIR%\media\EFI\BOOT\bootx64.efi" >NUL
)

if exist "%WINPE_DIR%\media\EFI\BOOT\bootaa64.efi" (
  copy "%BOOTMGRPATH%" "%WINPE_DIR%\media\EFI\BOOT\bootaa64.efi" >NUL
)

copy "%BOOTMGRPATH%" "%WINPE_DIR%\media\EFI\MICROSOFT\BOOT\bootmgfw.efi" >NUL

REM Make sure the destination refers to a storage drive,
REM and is not any other type of path
echo %DEST%| findstr /B /E /I "[A-Z]:" >NUL
if errorlevel 1 (
  echo ERROR: Destination needs to be a disk drive, e.g F:.
  goto fail
)

REM Make sure the destination path exists
if not exist "%DEST%" (
  echo ERROR: Destination drive "%DEST%" does not exist.
  goto fail
)

REM Set the boot code on the volume using bootsect.exe
echo Setting the boot code on %DEST%...
echo.
bootsect.exe /nt60 %DEST% /force /mbr >NUL
if errorlevel 1 (
  echo ERROR: Failed to set the boot code on %DEST%.
  goto fail
)

REM We first decompress the source directory that we are copying from.
REM  This is done to work around an issue with xcopy when working with
REM  compressed NTFS source directory.
REM
REM Note that this command will not cause an error on file systems that
REM  do not support compression - because we do not use /f.
compact /u "%WINPE_DIR%\media" >NUL
if errorlevel 1 (
  echo ERROR: Failed to decompress "%WINPE_DIR%\media".
  goto fail
)

REM Copy the media files from the user-specified working directory
echo Copying files to %DEST%...
echo.
xcopy /herky "%WINPE_DIR%\media\*.*" "%DEST%\" >NUL
if errorlevel 1 (
  echo ERROR: Failed to copy files to "%DEST%\".
  goto fail
)

echo.
echo ====================================
echo Setting volume label...
echo ====================================
label %DRIVE_LETTER%: TinyWin11

echo.
echo ====================================
echo Copying resources...
echo ====================================
copy /y dist\shell\shell.exe %DRIVE_LETTER%:\
xcopy /q /y /e dist\shell\shell_data %DRIVE_LETTER%:\shell_data\
rmdir /s /q %DRIVE_LETTER%:\shell_data\userprofile\Fonts
copy /y tinywin11\autoexec.bat %DRIVE_LETTER%:\shell_data\userprofile\AppData\
copy /y tinywin11\config.pson %DRIVE_LETTER%:\shell_data\userprofile\AppData\
copy /y tinywin11\quick_launch.pson %DRIVE_LETTER%:\shell_data\userprofile\AppData\
copy /y tinywin11\start_menu.pson %DRIVE_LETTER%:\shell_data\userprofile\AppData\
del /q %DRIVE_LETTER%:\shell_data\userprofile\AppData\icon_cache\*

mkdir %DRIVE_LETTER%:\programs
xcopy /q /y /e tinywin11\programs\7-Zip       %DRIVE_LETTER%:\programs\7-Zip\
xcopy /q /y /e tinywin11\programs\Explorer++  %DRIVE_LETTER%:\programs\Explorer++\
xcopy /q /y /e tinywin11\programs\IrfanView   %DRIVE_LETTER%:\programs\IrfanView\
xcopy /q /y /e tinywin11\programs\Notepad++   %DRIVE_LETTER%:\programs\Notepad++\
xcopy /q /y /e tinywin11\programs\OpenWith    %DRIVE_LETTER%:\programs\OpenWith\
xcopy /q /y /e tinywin11\programs\SumatraPDF  %DRIVE_LETTER%:\programs\SumatraPDF\
xcopy /q /y /e tinywin11\programs\SwiftSearch %DRIVE_LETTER%:\programs\SwiftSearch\
xcopy /q /y /e tinywin11\programs\Windows     %DRIVE_LETTER%:\programs\Windows\
xcopy /q /y /e tinywin11\programs\WordPad     %DRIVE_LETTER%:\programs\WordPad\

copy /y tinywin11\autorun.inf %DRIVE_LETTER%:\

echo.
echo ====================================
echo Zeroing free disk space...
echo ====================================
sdelete64.exe -z %DRIVE_LETTER%:

echo.
echo ====================================
echo Unmounting VHD disk image...
echo ====================================
(echo select vdisk file="%VHD_FILE%" & echo detach vdisk & echo exit) | diskpart

echo.
echo ====================================
echo Removing VHD footer...
echo ====================================
fsutil file seteof %VHD_FILE% %IMG_SIZE%
ren %VHD_FILE% %BASENAME%.img

echo.
echo ====================================
echo Creating VMDK disk image...
echo ====================================
qemu-img.exe convert -f raw "%IMG_FILE%" -O vmdk "%VMDK_FILE%"

echo.
echo Done.

goto cleanup

:fail
set EXITCODE=1
goto cleanup

:cleanup
endlocal & exit /b %EXITCODE%
