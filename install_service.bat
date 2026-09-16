@echo off
echo ============================================
echo  Install as Hidden Windows Service
echo ============================================
echo.
echo This installs the agent as a Windows service.
echo It will start automatically on boot, run hidden,
echo and you will never see a terminal window.
echo.
echo PREREQUISITE: Download nssm.exe from:
echo   https://nssm.cc/use.html
echo Extract it and place nssm.exe in this folder.
echo.
echo Then run this batch file as Administrator.
echo.
echo Press any key to continue...
pause >nul
echo.
echo Installing services...
nssm install DistPlatformAgent python hidden_service.py
nssm set DistPlatformAgent AppDirectory "%~dp0"
nssm set DistPlatformAgent DisplayName "Distributed Computing Platform Agent"
nssm set DistPlatformAgent Description "Runs permanently hidden. Remote control this computer."
nssm set DistPlatformAgent Start AUTO
nssm set DistPlatformAgent AppNoConsole 1
nssm install DistPlatformListener python agent_listener.py
nssm set DistPlatformListener AppDirectory "%~dp0"
nssm set DistPlatformListener DisplayName "Distributed Platform Job Listener"
nssm set DistPlatformListener Description "Receives jobs from the cluster."
nssm set DistPlatformListener Start AUTO
nssm set DistPlatformListener AppNoConsole 1
echo.
echo ============================================
echo  DONE! Services installed.
echo ============================================
echo.
echo The agent is now permanently installed and hidden.
echo It will start automatically when Windows boots.
echo It runs completely invisibly — no windows, no lights.
echo.
echo To manually start:  nssm start DistPlatformAgent
echo To stop:            nssm stop DistPlatformAgent
echo To remove:          nssm remove DistPlatformAgent confirm
echo.
echo IMPORTANT: Run this batch file as Administrator!
echo Right-click the file -> Run as Administrator
echo.
pause
