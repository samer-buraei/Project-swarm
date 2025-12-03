@echo off
echo ===================================================
echo           FIRE SWARM DEMO LAUNCHER
echo ===================================================
echo.

:: Find Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python from python.org
    pause
    exit /b
)

echo [1/3] Installing dependencies...
python -m pip install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may have failed to install.
)
echo      Done.

echo.
echo [2/3] Launching Dashboard (browser)...
start "Fire Swarm Dashboard" cmd /c "python -m streamlit run dashboard.py --server.headless true"

:: Wait for dashboard to start
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Launching Drone Simulation (camera window)...
echo.
echo ===================================================
echo   CONTROLS:
echo     Press 'f' = Simulate FIRE detection
echo     Press 'q' = Quit simulation
echo.
echo   The browser dashboard will show:
echo     - Real-time drone camera feed
echo     - GPS map with drone position
echo     - Fire detection alerts
echo ===================================================
echo.

:: Run simulation in foreground so user can see output
python simulation.py

echo.
echo Simulation ended. Press any key to close...
pause >nul
