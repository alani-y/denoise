@echo off
REM ---------------------------------------------------------------
REM Builds Denoiser.exe from the current source using PyInstaller.
REM Run this from the project folder (double-click or `build.bat`).
REM ---------------------------------------------------------------

echo.
echo === Denoiser build script ===
echo.

REM --- Check Python is available -----------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found on PATH.
    echo Install Python 3.10+ from https://www.python.org/downloads/
    echo and make sure "Add python.exe to PATH" is checked during install.
    pause
    exit /b 1
)

REM --- Install/upgrade build + runtime dependencies -----------------
echo Installing dependencies...
python -m pip install --upgrade pip >nul
pip install --upgrade pyinstaller opencv-python-headless pyyaml numpy
if errorlevel 1 (
    echo ERROR: pip install failed. See output above.
    pause
    exit /b 1
)

REM --- Clean previous build artifacts --------------------------------
echo.
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM --- Build ----------------------------------------------------------
echo.
echo Building executable with PyInstaller...
pyinstaller build.spec --noconfirm
if errorlevel 1 (
    echo ERROR: PyInstaller build failed. See output above.
    pause
    exit /b 1
)

REM --- Copy config + create expected folders next to the exe ----------
echo.
echo Copying config.yaml and creating images folders next to the exe...
copy /Y config.yaml dist\config.yaml >nul
if not exist dist\images\input mkdir dist\images\input
if not exist dist\images\output mkdir dist\images\output

echo.
echo === Build complete ===
echo Executable: dist\Denoiser.exe
echo Config:     dist\config.yaml
echo Drop images into dist\images\input and run Denoiser.exe
echo.
pause