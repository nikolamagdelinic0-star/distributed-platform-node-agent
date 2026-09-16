DEPLOYMENT INSTRUCTIONS - Distributed Computing Platform
==========================================================

CONTROLLER IS ALREADY RUNING ON THIS MACHINE.
Access the dashboard at:
  https://dp-platform-2026.loca.lt/static/index.html
Login: admin / admin_default_change_me

==============================================================
SECTION 1: INSTALL THE AGENT ON ANY OTHER COMPUTER
==============================================================

EVERY STEP BELOW MUST BE DONE ON THE COMPUTER YOU WANT TO ADD.

STEP 1: Download the agent files.
Open a terminal/command prompt on that computer and type:

  git clone https://github.com/nikolamagdelinic0-star/distributed-platform-node-agent.git

Wait for it to download. Then type:

  cd distributed-platform-node-agent

STEP 2: Install Python 3.10 or later.
Go to https://python.org/downloads/
Download Python 3.10+.
Run the installer.
ON THE FIRST SCREEN, CHECK THE BOX that says "Add Python to PATH".
Click "Install Now".
Close the installer.
To verify: type "python --version" in the terminal. Should show "Python 3.x.x".
If it shows an error, redo Step 2 and CHECK THE PATH BOX.

STEP 3: Install dependencies.
In the terminal (still in the distributed-platform-node-agent folder), type:

  pip install psutil requests

Wait for it to finish.

STEP 4: Configure the agent.
Open agent_config.txt in Notepad or any text editor.
It should already say:
  CONTROLLER_URL=https://dp-platform-2026.loca.lt
If not, change it to exactly that and save.

STEP 5: Run the agent.
In the terminal, type:

  python agent.py

You should see:
  Node Agent starting on node-...
  Node Agent started successfully

Leave this terminal open. The agent must keep running.

STEP 6: Approve in the dashboard.
On your phone or any device, go to:
  https://dp-platform-2026.loca.lt/static/index.html
Login: admin / admin_default_change_me
Find the new computer marked PENDING. Click it. Click Approve.
Status changes to ONLINE.

STEP 7: MAKE IT RUN PERMANENTLY (no terminal needed).
After Step 5 works, press Ctrl+C to stop the agent.
Then type:

  python auto_start.py

This creates a shortcut that auto-starts the agent when Windows boots.
The agent will now run permanently without any terminal window.

OR to make it a proper Windows service (requires nssm from nssm.cc):
  python install_as_service.py
  Then: nssm start DistPlatformAgent

Repeat Steps 1-7 for every computer you want to add.

==============================================================
SECTION 2: WHAT YOU CAN DO WITH THE DASHBOARD
==============================================================

Open https://dp-platform-2026.loca.lt/static/index.html on any device.
Login: admin / admin_default_change_me

DASHBOARD TAB:
- See total cluster power (all CPUs, all RAM, all GPUs combined)
- Shows how many nodes are online, busy, idle

NODES TAB:
- See every computer's specs
- Each shows CPU, RAM, GPU, storage, status
- Click "Remote Desktop" button on any node
- Click "Approve" on pending nodes

REMOTE TAB:
- Remote desktop control of any node
- Terminal access to any node
- File transfer

JOBS TAB:
- Submit compute jobs to the cluster
- Jobs are distributed across available nodes
- Combined power of all nodes used together

MODELS TAB:
- Import AI models
- Train models using cluster GPU power
- Deploy models

==============================================================
SECTION 3: HOW IT WORKS
==============================================================

- Your controller runs permanently with a watchdog that restarts it if it crashes
- The tunnel (dp-platform-2026.loca.lt) keeps the controller accessible from anywhere
- Each agent connects to the controller and reports its hardware
- Agents auto-start on Windows boot (no terminal needed)
- You can add unlimited computers — each one adds more power to the cluster
- Combined computing power = sum of all nodes
- You control everything from one dashboard, on any device, anywhere

==============================================================
TROUBLESHOOTING
==============================================================

If the agent shows "Heartbeat returned 405":
- Restart the agent: python agent.py
- The server has been updated to fix this

If the dashboard shows 401 error:
- Clear browser cache (Ctrl+Shift+Delete)
- Hard refresh the page
- Login again

If the tunnel shows "Tunnel Unavailable":
- The watchdog automatically restarts it
- Wait 30 seconds and try again

If the agent stops running:
- Run: python auto_start.py to auto-start on boot
- Or run: python agent.py manually in terminal

==============================================================
GitHub Repository: https://github.com/nikolamagdelinic0-star/distributed-platform-node-agent
Controller Dashboard: https://dp-platform-2026.loca.lt/static/index.html
