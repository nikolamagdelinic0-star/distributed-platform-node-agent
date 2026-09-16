@echo off
echo ================================================
echo   Distributed Computing Platform
echo   Node Agent Installer for Windows
echo ================================================
echo.
echo This installs the node agent on this computer.
echo The node connects to the central controller and
echo shares its computing power with the cluster.
echo.
echo ================================================
echo.

echo Step 1: Check Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed.
    echo Download from https://www.python.org/downloads/
    echo Install it, check "Add Python to PATH"
    echo Then run this installer again.
    pause
    exit /b 1
)
echo Python found.

echo.
echo Step 2: Install dependencies...
pip install psutil requests

echo.
echo Step 3: Configure controller address...
echo IMPORTANT: Edit agent_config.txt to set the
echo correct CONTROLLER_URL for your network.
echo The controller IP is shown below.
echo.
echo Check the main computer's IP by running this on it:
echo   hostname -I  (Linux/Mac)
echo   ipconfig     (Windows)
echo.
echo After editing agent_config.txt, proceed.
echo.
echo Step 4: Start the agent...
echo Run: python agent.py
echo The agent will register with the controller.
echo.
echo ================================================
echo Installation complete!
echo To start the agent: python agent.py
echo ================================================
echo.
pause
