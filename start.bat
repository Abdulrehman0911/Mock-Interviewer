@echo off
title MockMate Launcher

echo =====================================
echo   MockMate - Starting servers...
echo =====================================
echo.

echo [1/2] Starting Backend (Flask)...
start "MockMate Backend" cmd /k "cd /d %~dp0backend && ..\.venv\Scripts\python app.py"

echo     Waiting for backend to load models...
timeout /t 8 /nobreak >nul

echo [2/2] Starting Frontend (Vite)...
start "MockMate Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo     Waiting for frontend to compile...
timeout /t 6 /nobreak >nul

echo.
echo =====================================
echo   MockMate is running!
echo   Opening http://localhost:5173
echo =====================================
echo.
start http://localhost:5173

echo Both servers are running in separate windows.
echo Close those windows to stop MockMate.
echo.
pause
