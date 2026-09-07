@echo off
setlocal

for %%I in ("%~dp0..") do set "APP_ROOT=%%~fI"
set "TAILSCALE_EXE=C:\Program Files\Tailscale\tailscale.exe"
set "PUBLIC_URL=https://by9000p.tail26d033.ts.net/"

call "%~dp0debug-windows.cmd" --check
if errorlevel 1 exit /b 1

if /I "%~1"=="--check" (
  if not exist "%TAILSCALE_EXE%" (
    echo [ERROR] Tailscale is not installed at "%TAILSCALE_EXE%".
    exit /b 1
  )
  echo One-click startup prerequisites are ready.
  exit /b 0
)

call "%~dp0debug-windows.cmd"
if errorlevel 1 exit /b 1

echo Configuring Tailscale Funnel for Vite on port 5173...
"%TAILSCALE_EXE%" funnel --bg 5173 >nul 2>&1
if errorlevel 1 (
  echo Administrator approval is required for Tailscale Funnel.
  powershell.exe -NoProfile -Command "Start-Process -FilePath '%TAILSCALE_EXE%' -Verb RunAs -ArgumentList 'funnel','--bg','5173' -Wait"
  if errorlevel 1 (
    echo [ERROR] Tailscale Funnel configuration failed.
    exit /b 1
  )
)

echo Waiting for API and Web readiness...
for /L %%I in (1,1,30) do (
  curl.exe --fail --silent --output NUL http://127.0.0.1:8000/api/v1/health 2>nul && curl.exe --fail --silent --output NUL http://127.0.0.1:5173/ 2>nul && goto ready
  timeout /t 1 /nobreak >nul
)

echo [ERROR] Services did not become ready within 30 seconds.
exit /b 1

:ready
echo.
echo SCUT Senior is ready.
echo Local:  http://localhost:5173/
echo Public: %PUBLIC_URL%
start "" "%PUBLIC_URL%"
endlocal
