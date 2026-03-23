@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"
set "VENV_PY=%SCRIPT_DIR%\.venv\Scripts\python.exe"
set "API_LOG=%SCRIPT_DIR%\logs\api.log"

echo ======================================================================
echo   BSLO - Bengaluru Strategic Logistics Optimizer
echo   Starting API Server and Dashboard
echo ======================================================================
echo.

set "PYTHON_CMD="
where python >nul 2>&1 && set "PYTHON_CMD=python"
if not defined PYTHON_CMD (
    where py >nul 2>&1 && set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    echo [ERROR] Python was not found in PATH.
    echo Install Python 3 and re-run this script.
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Virtual environment not found. Creating...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )

    "%VENV_PY%" -m pip install --upgrade pip
    if errorlevel 1 (
        echo [ERROR] Failed to upgrade pip.
        exit /b 1
    )

    "%VENV_PY%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install requirements.
        exit /b 1
    )
)

if not exist "models\xgboost_tuned.pkl" (
    echo [ERROR] Trained model not found.
    echo Run the XGBoost modeling notebook first:
    echo   jupyter notebook notebooks\03_xgboost_modeling.ipynb
    exit /b 1
)

echo [OK] Models found
echo.

if not exist "logs" mkdir logs >nul 2>&1

echo [INFO] Starting API Server on http://localhost:8000
start "BSLO_API" cmd /c ""%VENV_PY%" -m uvicorn src.api:app --host 0.0.0.0 --port 8000 1>"%API_LOG%" 2>&1"

set /a WAIT_SEC=0
:wait_api
powershell -NoProfile -Command "try { $r = Invoke-WebRequest -UseBasicParsing http://localhost:8000/health -TimeoutSec 3; if ($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if not errorlevel 1 goto api_running

set /a WAIT_SEC+=1
if !WAIT_SEC! GEQ 20 goto api_failed
timeout /t 1 /nobreak >nul
goto wait_api

:api_failed
echo [ERROR] API Server failed to start.
if exist "logs\api.log" (
    echo -------- API LOG (last 40 lines) --------
    powershell -NoProfile -Command "Get-Content -Path 'logs\\api.log' -Tail 40"
    echo -----------------------------------------
)
taskkill /FI "WINDOWTITLE eq BSLO_API*" /T /F >nul 2>&1
exit /b 1

:api_running
echo [OK] API Server is running
echo.
echo [INFO] Starting Streamlit Dashboard on http://localhost:8501
echo.
echo ======================================================================
echo   Access Points:
echo   - API Documentation: http://localhost:8000/docs
echo   - Dashboard:         http://localhost:8501
echo   - API Health:        http://localhost:8000/health
echo ======================================================================
echo.
echo Press Ctrl+C to stop the dashboard. API will be stopped automatically.
echo.

"%VENV_PY%" -m streamlit run app\streamlit_app.py

echo.
echo [INFO] Stopping API Server...
taskkill /FI "WINDOWTITLE eq BSLO_API*" /T /F >nul 2>&1
echo [OK] Shutdown complete

endlocal
exit /b 0
