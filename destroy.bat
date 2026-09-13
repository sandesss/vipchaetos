@echo off
title VIP Lock Screen Destroyer
cls
echo ========================================================
echo       VIP LOCK SCREEN REMOVER & CLEANUP TOOL
echo ========================================================
echo.
set /p pass="Ilagay ang VIP Password para i-delete ang lock screen: "

if "%pass%"=="VIP123" (
    echo.
    echo [+] Tamang Password! Nililinis ang sistema...
    
    :: 1. Tanggalin sa Windows Registry Startup
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsSysDefender" /f >nul 2>&1
    
    :: 2. Alisin ang Hidden at System attributes ng shadow file para mabura
    attrib -h -s "%APPDATA%\Microsoft\Windows\Themes\Cache\sys_update.exe" >nul 2>&1
    
    :: 3. Burahin ang mismong file
    del /f /q "%APPDATA%\Microsoft\Windows\Themes\Cache\sys_update.exe" >nul 2>&1
    
    :: 4. I-kill ang anumang natirang background process ng vip o sys_update
    taskkill /f /im vip.exe >nul 2>&1
    taskkill /f /im sys_update.exe >nul 2>&1

    echo.
    echo [SUCCESSS] Nabura na ang lahat ng lock screen files at registry entries!
    echo Pwede mo nang i-close ang window na ito.
    pause
) else (
    echo.
    echo [X] MALI ANG PASSWORD! Hindi mabubura ang mga file.
    pause
)