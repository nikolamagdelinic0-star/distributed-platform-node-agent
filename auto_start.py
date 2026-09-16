"""Windows startup helper - creates a shortcut in Startup folder."""
import os
import sys
import shutil
import glob

def create_startup_shortcut():
    """Create a shortcut to auto-start the agent on Windows boot."""
    desktop = os.path.expanduser("~")
    startup = os.path.join(desktop, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
    os.makedirs(startup, exist_ok=True)
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.py")
    shortcut_path = os.path.join(startup, "Distributed Platform Agent.lnk")
    
    # Create a VBScript to run python hidden
    vbs_path = os.path.join(startup, "Distributed Platform Agent.vbs")
    vbs_content = f'''
Set objShell = CreateObject("WScript.Shell")
objShell.Run "python """ + "{script_path}" + """", 0, False
'''
    with open(vbs_path, 'w') as f:
        f.write(vbs_content)
    
    print(f"Created startup shortcut: {vbs_path}")
    print("The agent will now auto-start when Windows boots.")
    print("To remove it, delete the .vbs file from Startup folder.")

if __name__ == "__main__":
    create_startup_shortcut()
