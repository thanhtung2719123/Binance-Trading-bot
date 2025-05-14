@echo off
REM === Trading Bot Installer and Builder ===

REM Create and activate a virtual environment (optional but recommended)
python -m venv venv
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Install TA-Lib (if not already installed)
pip install --use-pep517 TA-Lib

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Build the executable
pyinstaller trading_bot.spec --clean

echo.
echo Build complete! Your executable is in the dist folder.
pause 