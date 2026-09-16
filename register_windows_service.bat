@echo off
echo ============================================
echo  Install Node Agent as Windows Service
echo ============================================
echo.
echo This will install the agent as a Windows
echo service that starts automatically.
echo.
echo Requirements: nssm (https://nssm.cc)
echo.
echo 1. Download nssm from https://nssm.cc/use.html
echo 2. Extract nssm.exe to this folder
echo 3. Run this batch file as Administrator
echo.
pause
nssm install DistributedPlatformAgent python agent.py
nssm set DistributedPlatformAgent AppDirectory "%~dp0"
nssm set DistributedPlatformAgent DisplayName "Distributed Computing Platform Agent"
nssm set DistributedPlatformAgent Start AUTO
nssm start DistributedPlatformAgent
echo.
echo Service installed! The agent now runs permanently.
echo.
pause
