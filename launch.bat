@echo off
REM Windows launcher script for the FastAPI + Next.js Dashboard System

setlocal enabledelayedexpansion

REM Colors for output (Windows compatible)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Function to print colored output
:log
set level=%1
shift
if "%level%"=="ERROR" (
    echo %RED%[ERROR]%NC% %*
) else if "%level%"=="SUCCESS" (
    echo %GREEN%[SUCCESS]%NC% %*
) else if "%level%"=="WARNING" (
    echo %YELLOW%[WARNING]%NC% %*
) else if "%level%"=="INFO" (
    echo %BLUE%[INFO]%NC% %*
) else (
    echo %*
)
goto :eof

REM Check if Python is available
:check_python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :python_found
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :python_found
)

call :log ERROR "Python not found. Please install Python 3.8 or higher."
exit /b 1

:python_found
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i
call :log INFO "Using Python %PYTHON_VERSION%"
goto :eof

REM Main function
:main
call :log INFO "🚀 Unified Backend & Frontend Launcher"

REM Check for Python
call :check_python

REM Run the Python launcher with all arguments
%PYTHON_CMD% launcher.py %*

goto :eof

REM Run main function
call :main %*
