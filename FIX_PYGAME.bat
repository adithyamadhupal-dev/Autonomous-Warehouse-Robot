@echo off
setlocal
title Fix Pygame Installation

echo Checking for Python 3.10...
py -3.10 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3.10"
    goto install
)

echo Checking for Python 3.11...
py -3.11 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3.11"
    goto install
)

echo Checking for Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3.12"
    goto install
)

echo.
echo No compatible Python version was found.
echo Install Python 3.12 and then run this file again.
pause
exit /b 1

:install
echo.
echo Using:
%PYTHON_CMD% --version
echo.
%PYTHON_CMD% -m pip install --upgrade pip setuptools wheel
%PYTHON_CMD% -m pip uninstall pygame -y
%PYTHON_CMD% -m pip install pygame==2.6.1

if errorlevel 1 (
    echo.
    echo Installation failed.
    pause
    exit /b 1
)

echo.
echo Pygame installed successfully.
echo Starting the project...
%PYTHON_CMD% warehouse_robot.py
pause
endlocal
