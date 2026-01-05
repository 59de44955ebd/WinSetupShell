@echo off
for /f "delims=" %%a in ('hostname') do set hostname=%%a
for /f "delims=[] tokens=2" %%a in ('ping -4 -n 1 %hostname% ^| findstr [') do echo %%a
