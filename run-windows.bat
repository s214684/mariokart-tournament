@echo off
SETLOCAL ENABLEDELAYEDEXECUTION

REM Build and run the app in Docker, then open browser on Windows
where docker >nul 2>nul
IF ERRORLEVEL 1 (
  echo Docker Desktop is not installed or not in PATH.
  echo Please install Docker Desktop for Windows and try again.
  pause
  exit /b 1
)

echo Building Docker image...
docker compose version >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
  docker compose build
) ELSE (
  docker-compose build
)
IF ERRORLEVEL 1 (
  echo Build failed.
  pause
  exit /b 1
)

echo Starting container...
docker compose version >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
  docker compose up -d
) ELSE (
  docker-compose up -d
)
IF ERRORLEVEL 1 (
  echo Failed to start container.
  pause
  exit /b 1
)

echo Waiting for the app to boot...
timeout /t 3 >nul

REM Open default browser at localhost:8000
start http://localhost:8000/

echo App is running. Press any key to stop and remove the container.
pause >nul

docker compose version >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
  docker compose down
) ELSE (
  docker-compose down
)

ENDLOCAL
exit /b 0