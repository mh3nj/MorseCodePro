@echo off
title Morse Code Pro - Professional Morse Suite
color 0A

setlocal enabledelayedexpansion

REM Store the starting directory
set STARTDIR=%CD%

echo      Morse Code Pro v1.5 Setup
echo    Professional Morse Code Suite
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.11+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check Python version (must be 3.11+)
for /f "tokens=2 delims= " %%v in ('python --version') do set PYVER=%%v
for /f "tokens=1,2 delims=." %%a in ("!PYVER!") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if !MAJOR! LSS 3 (
    echo [ERROR] Python 3.11+ is required. Detected: !PYVER!
    pause
    exit /b 1
)
if !MAJOR! EQU 3 if !MINOR! LSS 11 (
    echo [ERROR] Python 3.11+ is required. Detected: !PYVER!
    echo You have Python !PYVER!. Please upgrade to 3.11 or higher.
    pause
    exit /b 1
)

echo [OK] Python found: !PYVER!
echo.

REM Check for Git (optional - only for updates)
git --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Git not found. Will use existing files only.
    set GIT_AVAILABLE=0
) else (
    echo [OK] Git found
    git --version
    set GIT_AVAILABLE=1
)
echo.

REM Check if MorseCodePro directory exists
if exist "MorseCodePro" (
    cd MorseCodePro
    echo [INFO] Found existing MorseCodePro directory
    
    if !GIT_AVAILABLE! EQU 1 (
        echo [UPDATE] Pulling latest changes...
        git pull origin main
        if errorlevel 1 (
            echo [WARN] Git pull failed, continuing with existing files...
        ) else (
            echo [OK] Successfully updated to latest version
        )
    )
) else (
    if !GIT_AVAILABLE! EQU 1 (
        echo [DOWNLOAD] Cloning repository...
        git clone https://github.com/mh3nj/MorseCodePro.git
        if errorlevel 1 (
            echo [ERROR] Failed to clone repository!
            echo Please check your internet connection or download manually
            pause
            exit /b 1
        )
        echo [OK] Repository cloned successfully
        cd MorseCodePro
    ) else (
        echo [ERROR] MorseCodePro directory not found and Git not available!
        echo Please download the source code manually from GitHub
        pause
        exit /b 1
    )
)

echo.
echo [SETUP] Setting up Python virtual environment...

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment!
        cd /d "%STARTDIR%"
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment!
    cd /d "%STARTDIR%"
    pause
    exit /b 1
)

echo [OK] Virtual environment activated
echo.

REM Check for requirements.txt
if not exist requirements.txt (
    echo [ERROR] requirements.txt not found!
    cd /d "%STARTDIR%"
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo [INSTALL] Installing/updating dependencies...
echo This may take a few minutes on first run...
echo.

python -m pip install --upgrade pip

REM Install core dependencies first
echo Installing core dependencies...
pip install customtkinter numpy scipy

REM Install audio dependencies with fallbacks
echo Installing audio dependencies...
pip install sounddevice soundfile simpleaudio pyttsx3

REM Install optional dependencies (continue if fail)
echo Installing optional dependencies...
pip install matplotlib pydub keyboard 2>nul

if errorlevel 1 (
    echo [WARN] Some optional dependencies failed to install
    echo The app will still work with core features
) else (
    echo [OK] All dependencies installed successfully
)

echo.
echo [LAUNCH] Starting Morse Code Pro...
echo.
echo    Setup Complete! Launching App...
echo.

REM Start the application
python main.py

echo.
echo [DONE] Thanks for using Morse Code Pro!
echo You can re-run this file anytime to update and launch the app.
echo.
echo Press any key to exit...
pause >nul

REM Return to original directory
cd /d "%STARTDIR%"
endlocal