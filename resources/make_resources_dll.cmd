@echo off

cd /d %~dp0

python make_resources_py.py

set PATH=C:\Program Files (x86)\Microsoft Visual Studio 10.0\Common7\IDE\;C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\BIN;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.0A\bin;%PATH%

set INCLUDE=C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\INCLUDE;C:\Program Files (x86)\Microsoft Visual Studio 10.0\VC\ATLMFC\INCLUDE;C:\Program Files (x86)\Microsoft SDKs\Windows\v7.0A\include;

rc /nologo /fo resources.res resources.rc
link /nologo /dll /NOENTRY /MACHINE:X86 resources.res /OUT:..\resources.dll

del /Q *.res

::if "%ERRORLEVEL%" NEQ "0" pause
pause
