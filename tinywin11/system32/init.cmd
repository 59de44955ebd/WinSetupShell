@echo off

reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "RecycleBinDrives" /t REG_DWORD /d 4294967295 /f

REM wpeinit

for %%a in (C D E F G H I J K L M N O P Q R S T U V W X Y Z) do if exist %%a:\shell.exe set SHELLDRIVE=%%a
start /wait "" %SHELLDRIVE%:\shell.exe
