@echo off
title Syllabus-Driven Exam Question Paper Generator
echo ======================================================================
echo    Syllabus-Driven Intelligent Exam Question Paper Generator
echo    CoreAlgorithm PROBLEM95 - Design and Analysis of Algorithms (DAA)
echo ======================================================================
echo.

:: Navigate to script directory
cd /d "%~dp0"

echo [1/2] Verifying Python dependencies...
python -m pip install -r requirements.txt --quiet

echo.
echo [2/2] Starting Flask Application Server...
echo Application URL: http://127.0.0.1:5000
echo.
echo Opening your web browser automatically...
start http://127.0.0.1:5000

echo.
echo ======================================================================
echo   Server is active! Press Ctrl+C in this terminal window to stop.
echo ======================================================================
python app.py
pause
