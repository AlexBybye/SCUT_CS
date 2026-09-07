@echo off
setlocal

for %%I in (git.exe) do set "GIT_EXE=%%~$PATH:I"
if not defined GIT_EXE (
  echo [ERROR] Git was not found on PATH.
  exit /b 1
)

for %%I in ("%GIT_EXE%") do set "GIT_CMD_DIR=%%~dpI"
for %%I in ("%GIT_CMD_DIR%..") do set "GIT_ROOT=%%~fI"
set "BASH_EXE=%GIT_ROOT%\bin\bash.exe"
for %%I in ("%~dp0..") do set "APP_ROOT=%%~fI"

if not exist "%BASH_EXE%" (
  echo [ERROR] Git Bash was not found at "%BASH_EXE%".
  exit /b 1
)
if not exist "%APP_ROOT%\.local\env.online" (
  echo [ERROR] Missing "%APP_ROOT%\.local\env.online".
  exit /b 1
)
if not exist "%APP_ROOT%\api\.venv\Scripts\python.exe" (
  echo [ERROR] Missing API virtual environment. Run uv sync first.
  exit /b 1
)
if not exist "%APP_ROOT%\web\node_modules\.bin\vite.cmd" (
  echo [ERROR] Missing Web dependencies. Run npm --prefix web ci first.
  exit /b 1
)

if /I "%~1"=="--check" (
  echo Environment and dependencies are ready.
  exit /b 0
)

start "SCUT Senior API" /D "%APP_ROOT%" "%BASH_EXE%" -lc "set -a; source .local/env.online; set +a; export SCUT_SENIOR_RETRIEVAL_MODE=local_corpus; exec ./api/.venv/Scripts/python.exe -m uvicorn scut_senior_api.main:app --reload --host 127.0.0.1 --port 8000"
start "SCUT Senior Web" /D "%APP_ROOT%\web" "%BASH_EXE%" -lc "exec ./node_modules/.bin/vite.cmd --host 0.0.0.0 --port 5173"

if /I "%~1"=="--funnel" (
  "C:\Program Files\Tailscale\tailscale.exe" funnel --bg 5173
  "C:\Program Files\Tailscale\tailscale.exe" funnel status
)

echo API:  http://127.0.0.1:8000
echo Web:  http://localhost:5173
echo Test: curl.exe http://127.0.0.1:8000/api/v1/health
endlocal
