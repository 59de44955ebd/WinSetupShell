@echo off

cd /d %~dp0

REM config
set APP_NAME=shell
set APP_DIR=%CD%\dist\%APP_NAME%\

REM cleanup
rmdir /s /q "dist\%APP_NAME%" 2>nul
del %APP_NAME%.exe 2>nul
rmdir /s /q %APP_NAME%_data 2>nul

REM "Compile" winapp constants
cd src
python _compile_const.py
cd ..
ren src\winapp\const.py __const.py
ren src\winapp\const_c.py const.py

echo.
echo ****************************************
echo Running pyinstaller...
echo ****************************************
pyinstaller --noupx -w -n "%APP_NAME%" -i NONE -r resources.dll -D src\main.py --contents-directory %APP_NAME%_data

ren src\winapp\const.py const_c.py
ren src\winapp\__const.py const.py

echo.
echo ****************************************
echo Copying resources...
echo ****************************************

xcopy /e app_data "dist\%APP_NAME%\shell_data\app_data\" >nul
xcopy /e bin "dist\%APP_NAME%\shell_data\bin\" >nul

echo.
echo ****************************************
echo Optimizing dist folder...
echo ****************************************

del "dist\%APP_NAME%\shell_data\libcrypto-3.dll"
del "dist\%APP_NAME%\shell_data\ucrtbase.dll"

echo.
echo ****************************************
echo Done.
echo ****************************************
echo.
pause
