#!/usr/bin/env bash
# ============================================================================
# Classroom Booking and Timetable Management System
# ============================================================================

set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================================"
echo "Classroom Booking and Timetable Management System"
echo "============================================================================"

# 1. Start Oracle 21c XE container if Docker is present
if command -v docker &> /dev/null; then
    echo "[INFO] Docker detected. Checking Oracle 21c container..."
    if ! docker ps -a --format '{{.Names}}' | grep -q "^oracle21c$"; then
        echo "[INFO] Running gvenzl/oracle-xe:21-slim container on port 1521..."
        docker run -d --name oracle21c -p 1521:1521 \
            -e ORACLE_PASSWORD="Classroom#2026" \
            -e APP_USER="CLASSROOM_APP" \
            -e APP_USER_PASSWORD="Classroom#2026" \
            gvenzl/oracle-xe:21-slim
    else
        docker start oracle21c || true
    fi
else
    echo "[INFO] Docker not present. Engaging embedded Oracle PL/SQL Engine."
fi

# 2. Virtual environment setup
if [ ! -d "venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 3. Launch Application
echo "============================================================================"
echo "[READY] Starting Flask application on http://localhost:5000"
echo "============================================================================"
export FLASK_APP=app.app
python3 -m flask run --host 0.0.0.0 --port 5000
