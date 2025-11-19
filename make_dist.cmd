@echo off
setlocal EnableDelayedExpansion
cd /d %~dp0

REM config
set APP_NAME=shell
set DIR=%CD%
set APP_DIR=%CD%\dist\%APP_NAME%\

REM cleanup
rmdir /s /q "dist\%APP_NAME%" 2>nul
del "dist\%APP_NAME%-x64-setup.exe" 2>nul
del "dist\%APP_NAME%-x64-portable.7z" 2>nul

REM "Compile" winapp contants
cd src
python _compile_const.py
cd ..
ren src\winapp\const.py __const.py
ren src\winapp\const_c.py const.py

echo.
echo ****************************************
echo Running pyinstaller...
echo ****************************************
set PYTHONPATH=%DIR%\..
pyinstaller --noupx -w -n "%APP_NAME%" -i NONE -r resources.dll -D src\main.py

ren src\winapp\const.py const_c.py
ren src\winapp\__const.py const.py

echo.
echo ****************************************
echo Copying resources...
echo ****************************************

xcopy /e app_data "dist\%APP_NAME%\_internal\app_data\" >nul
xcopy /e bin "dist\%APP_NAME%\_internal\bin\" >nul

mkdir "dist\%APP_NAME%\_internal\startup"


::xcopy /e resources "dist\%APP_NAME%\_internal\resources\" >nul
::copy resources\empty.bmp "dist\%APP_NAME%\_internal\resources\"
::copy resources\standard-icons-1.bmp "dist\%APP_NAME%\_internal\resources\"
::copy resources\standard-icons-2.bmp "dist\%APP_NAME%\_internal\resources\"
::copy resources\standard-icons-3.bmp "dist\%APP_NAME%\_internal\resources\"


echo.
echo ****************************************
echo Optimizing dist folder...
echo ****************************************

::del "dist\%APP_NAME%\_internal\api-ms-win-core-console-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-datetime-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-debug-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-errorhandling-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-file-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-file-l1-2-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-file-l2-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-handle-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-heap-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-interlocked-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-libraryloader-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-localization-l1-2-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-memory-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-namedpipe-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-processenvironment-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-processthreads-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-processthreads-l1-1-1.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-profile-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-rtlsupport-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-string-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-synch-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-synch-l1-2-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-sysinfo-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-timezone-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-util-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-conio-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-convert-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-environment-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-filesystem-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-heap-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-locale-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-math-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-process-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-runtime-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-stdio-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-string-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-time-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-crt-utility-l1-1-0.dll"
::del "dist\%APP_NAME%\_internal\api-ms-win-core-fibers-l1-1-0.dll"

del "dist\%APP_NAME%\_internal\libcrypto-3.dll"
del "dist\%APP_NAME%\_internal\ucrtbase.dll"


::copy /y dist\PyExplorer\PyExplorer.exe "dist\%APP_NAME%\"

::call :create_7z
::call :create_installer

:done
echo.
echo ****************************************
echo Done.
echo ****************************************
echo.
pause

endlocal
goto :eof

:create_7z
if not exist "C:\Program Files\7-Zip\" (
	echo.
	echo ****************************************
	echo 7z.exe not found at default location, omitting .7z creation...
	echo ****************************************
	exit /B
)
echo.
echo ****************************************
echo Creating .7z archive...
echo ****************************************
cd dist
set PATH=C:\Program Files\7-Zip;%PATH%
7z a "%APP_NAME%-x64-portable.7z" "%APP_NAME%\*"
cd ..
exit /B

:create_installer
if not exist "C:\Program Files (x86)\NSIS\" (
	echo.
	echo ****************************************
	echo NSIS not found at default location, omitting installer creation...
	echo ****************************************
	exit /B
)
echo.
echo ****************************************
echo Creating installer...
echo ****************************************

REM get length of APP_DIR
set TF=%TMP%\x
echo %APP_DIR%> %TF%
for %%? in (%TF%) do set /a LEN=%%~z? - 2
del %TF%

call :make_abs_nsh uninstall_list.nsh

del "%NSH%" 2>nul

cd "%APP_DIR%"

for /F %%f in ('dir /b /a-d') do (
	echo Delete "$INSTDIR\%%f" >> "%NSH%"
)

for /F %%d in ('dir /s /b /aD') do (
	cd "%%d"
	set DIR_REL=%%d
	for /F %%f IN ('dir /b /a-d 2^>nul') do (
		echo Delete "$INSTDIR\!DIR_REL:~%LEN%!\%%f" >> "%NSH%"
	)
)

cd "%APP_DIR%"

for /F %%d in ('dir /s /b /ad^|sort /r') do (
	set DIR_REL=%%d
	echo RMDir "$INSTDIR\!DIR_REL:~%LEN%!" >> "%NSH%"
)

cd "%DIR%"
set PATH=C:\Program Files (x86)\NSIS;%PATH%
makensis make-installer.nsi
exit /B

:make_abs_nsh
set NSH=%~dpnx1%
exit /B
