@echo off
REM === Run Trading Bot ===

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the trading bot
python -m trading_bot.main

pause 