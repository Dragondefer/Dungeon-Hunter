@echo off
REM Try to update via Git (if available)
where git >nul 2>nul && git pull

REM Run the game
python main.py

echo.
echo Press any key to exit...
pause >nul
