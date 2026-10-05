@echo off
REM baeumteo-data refresh: collect -> commit/push if changed.
REM API key is read from %USERPROFILE%\.baeumteo_key (kept out of this repo),
REM or from the LEARNING_API_KEY environment variable.
chcp 65001 >nul
cd /d "%~dp0"

if "%LEARNING_API_KEY%"=="" (
  if exist "%USERPROFILE%\.baeumteo_key" (
    set /p LEARNING_API_KEY=<"%USERPROFILE%\.baeumteo_key"
  )
)
if "%LEARNING_API_KEY%"=="" (
  echo [ERROR] LEARNING_API_KEY not set and key file missing.
  exit /b 1
)

echo [1/3] collecting...
python collect.py
if errorlevel 1 (
  echo [ERROR] collect failed.
  exit /b 1
)

echo [2/3] checking changes...
git add data/courses.json
git diff --cached --quiet
if %errorlevel%==0 (
  echo no change - skip push.
  exit /b 0
)

echo [3/3] commit / push...
for /f "tokens=*" %%d in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HH:mm"') do set NOW=%%d
git commit -m "data: refresh %NOW%"
git push
echo done.
