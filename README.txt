DEPLOYMENT INSTRUCTIONS - Distributed Computing Platform
==========================================================

THIS MACHINE IS THE CONTROLLER (SERVER).
Everything below is for OTHER computers you want to add.

QUICK START FOR EACH COMPUTER:
==============================

1. Copy the entire "node-agent" folder to the other computer.
   You can use USB, email, cloud storage, or any method.
   The folder contains:
   - agent.py (the main program)
   - agent_config.txt (configuration - MUST EDIT)
   - requirements.txt (dependencies)
   - install_for_windows.bat (Windows installer)
   - start.py (starter script)

2. On the other computer, install Python 3.10 or later.
   Download from: https://www.python.org/downloads/
   IMPORTANT: Check "Add Python to PATH" during installation.

3. Open a terminal/command prompt on the other computer.
   Navigate to the node-agent folder.

4. Edit agent_config.txt with a text editor.
   Change CONTROLLER_URL to the IP address of THIS computer
   (the one running the controller).
   Example: CONTROLLER_URL=http://192.168.1.50:8000

5. Install dependencies:
   pip install psutil requests

6. Start the agent:
   python agent.py

7. Go to http://CONTROLLER_IP:8000/static/index.html
   in your browser on ANY device.
   Login: admin / admin_default_change_me
   Find the node under "Nodes" and click "Approve".

DONE! The computer is now part of your cluster.
Repeat steps 1-7 for every other computer.

CONTROLLER IP:
Find the controller's IP by running this on it:
  Linux/Mac: hostname -I
  Windows:   ipconfig
Look for the IP address that starts with 192.168. or 10.

CONTROLLER IS ALREADY RUNING ON THIS MACHINE.
You can access the dashboard at:
  http://localhost:8000/static/index.html

