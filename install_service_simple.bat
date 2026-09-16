@echo off
echo ============================================
echo  Install as Windows Service
echo ============================================
echo.
echo Download nssm from https://nssm.cc/use.html
echo Extract nssm.exe to this folder.
echo Then run this as Administrator.
echo.
echo Press any key to continue...
pause >nul
echo Installing...
nssm install DistPlatformAgent python agent.py
nssm set DistPlatformAgent AppDirectory "%~dp0"
nssm set DistPlatformAgent DisplayName "Distributed Computing Platform Agent"
nssm set DistPlatformAgent Start AUTO
nssm install DistPlatformListener python agent_listener.py
nssm set DistPlatformListener AppDirectory "%~dp0"
nssm set DistPlatformListener DisplayName "Distributed Computing Platform Job Listener"
nssm set DistPlatformListener Start AUTO
echo.
echo Done! Both services installed and will start automatically.
echo.
pause
