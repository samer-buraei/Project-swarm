@echo off
echo ===================================================
echo           FIRE SWARM DEMO LAUNCHER
echo ===================================================
echo.

:: Find Python (check for py launcher)
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python Launcher 'py' not found.
    echo Please install Python from python.org and ensure 'py' is installed.
    pause
    exit /b
)

echo [1/4] Installing dependencies...
py -m pip install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may have failed to install.
)
echo      Done.

echo.
echo [2/4] Launching Fleet Dashboard (browser)...
start "Fleet Dashboard" cmd /c "cd app && py -m streamlit run dashboard_fleet_real.py --server.port 8506 --server.headless true"

echo.
echo [3/4] Launching Mission Planner (browser)...
start "Mission Planner" cmd /c "cd app && py -m streamlit run dashboard_mission.py --server.port 8507 --server.headless true"

:: Wait for dashboards to start
timeout /t 5 /nobreak >nul

echo.
echo [4/4] Launching Drone Fleet Simulation...
echo.
echo ===================================================
echo   CONTROLS:
echo     The fleet simulation will run in this window.
echo     Open http://localhost:8506 to control the fleet.
echo     Open http://localhost:8507 to plan missions.
echo ===================================================
echo.

cd app
py launch_fleet.py

echo.
echo Simulation ended. Press any key to close...
pause >nul
