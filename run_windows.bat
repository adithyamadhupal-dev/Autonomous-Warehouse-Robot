@echo off
setlocal
title Autonomous Warehouse Robot

echo ==========================================
echo   Autonomous Warehouse Robot Launcher
echo ==========================================
echo.

set "PYTHON_CMD="

REM Prefer compatible Python versions. Pygame may fail on very new Python versions.
py -3.10 --version >nul 2>&1
if %errorlevel%==0 set "PYTHON_CMD=py -3.10"

if not defined PYTHON_CMD (
    py -3.11 --version >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=py -3.11"
)

if not defined PYTHON_CMD (
    py -3.12 --version >nul 2>&1
    if %errorlevel%==0 set "PYTHON_CMD=py -3.12"
)

if not defined PYTHON_CMD (
    echo ERROR: Compatible Python 3.10, 3.11, or 3.12 was not found.
    echo.
    echo Your current default appears to be Python 3.14, which caused
    echo the Pygame installation failure.
    echo.
    echo Install Python 3.12 from python.org and enable:
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo Using:
%PYTHON_CMD% --version
echo.

echo Updating pip...
%PYTHON_CMD% -m pip install --upgrade pip

echo.
echo Installing Pygame...
%PYTHON_CMD% -m pip install pygame==2.6.1

if errorlevel 1 (
    echo.
    echo ERROR: Pygame installation failed.
    echo Try running FIX_PYGAME.bat.
    pause
    exit /b 1
)

echo.
echo Starting simulation...
%PYTHON_CMD% warehouse_robot.py

if errorlevel 1 (
    echo.
    echo The program stopped with an error.
)

pause
endlocal
