@echo off
REM Pull latest changes from the GitHub repository
git pull

REM Run the game
python main.py

echo.
echo Press any key to exit...
pause >nul
