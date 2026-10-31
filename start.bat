@echo off
setlocal enabledelayedexpansion

echo ============================================================================
echo Classroom Booking and Timetable Management System
echo ============================================================================

cd /d "%~dp0"

:: 1. Check Docker and Start Oracle XE Container if Docker is installed
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [INFO] Docker detected on host system.
    docker ps -a --filter "name=oracle21c" --format "{{.Names}}" | findstr /i "oracle21c" >nul
    if %errorlevel% neq 0 (
        echo [INFO] Creating and starting Oracle 21c XE container...
        docker run -d --name oracle21c -p 1521:1521 -e ORACLE_PASSWORD=Classroom#2026 -e APP_USER=CLASSROOM_APP -e APP_USER_PASSWORD=Classroom#2026 gvenzl/oracle-xe:21-slim
    ) else (
        echo [INFO] Starting existing Oracle 21c XE container...
        docker start oracle21c >nul 2>nul
    )
) else (
    echo [INFO] Docker daemon not active in environment.
    echo [INFO] Engaging high-fidelity embedded Oracle PL/SQL simulation engine.
)

:: 2. Set up Python Virtual Environment
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

:: 3. Launch Flask Web Application
echo ============================================================================
echo [READY] Launching Classroom Booking System on http://127.0.0.1:5000
echo ============================================================================
start "" http://127.0.0.1:5000/
python -m flask --app app.app run --host 0.0.0.0 --port 5000

pause
