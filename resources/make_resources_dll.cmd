@echo off
cd /d %~dp0
python make_resources_py.py
rc_compile\rc /nologo /fo resources.res resources.rc
rc_compile\link /nologo /dll /NOENTRY /MACHINE:X86 resources.res /OUT:..\resources.dll
del /Q *.res
pause
