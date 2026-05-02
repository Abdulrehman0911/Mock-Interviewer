@echo off
title MockMate

echo Starting MockMate...
echo.

start "MockMate Backend" cmd /k "cd /d d:\Projects\AI_Project\mock-interviewer\backend && python app.py"

timeout /t 4 /nobreak >nul

start "MockMate Frontend" cmd /k "cd /d d:\Projects\AI_Project\mock-interviewer\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo MockMate is starting...
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Opening browser...
start http://localhost:5173

echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
pause
