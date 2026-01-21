@echo off
echo Glitcher - Professional Web Security Testing Platform
echo.
echo Choose an option:
echo 1. Web Version (Node.js)
echo 2. GUI Version (Python)
echo.
choice /C 12 /M "Enter your choice"

if errorlevel 2 goto python
if errorlevel 1 goto node

:node
echo Starting Glitcher Web Version...
npm start
goto end

:python
echo Starting Glitcher Python GUI Version...
python run_glitcher.py
goto end

:end
pause