@echo off
setlocal

rem Use this after switching branches so API/Vite reload code and migrations.
rem It only stops listeners on this app's API and Vite ports.
if /I "%~1"=="--check" (
  call "%~dp0start-all-windows.cmd" --check
  exit /b %errorlevel%
)

for %%P in (8000 5173) do (
  for /f "tokens=5" %%I in ('netstat -ano ^| findstr /R /C:":%%P .*LISTENING"') do (
    echo Stopping process %%I on port %%P...
    taskkill /PID %%I /T /F >nul 2>&1
  )
)

timeout /t 2 /nobreak >nul
call "%~dp0start-all-windows.cmd"
exit /b %errorlevel%
