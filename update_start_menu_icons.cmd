@echo off

cd /d %~dp0

REM make sure that PROGRAMS env var is set
setx PROGRAMS %~dp0programs >nul

cd src
python _update_startmenu.py
cd ..
echo Done.
echo.
pause
