"""Create Windows Service for the agent — fully hidden, auto-starts on boot."""
import os
import sys
import subprocess
import shutil

def create_windows_service():
    """Create the agent as a Windows service using nssm."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python = sys.executable
    hidden_service = os.path.join(script_dir, "hidden_service.py")
    
    print("Checking for nssm...")
    nssm = shutil.which("nssm")
    
    if not nssm:
        print("nssm not found. You need to download it from https://nssm.cc/use.html")
        print("Download nssm-2.24.zip, extract nssm.exe to this folder.")
        print("Then run this script again.")
        print()
        print("ALTERNATIVE: Download nssm.exe and place it in:")
        print(f"  {script_dir}\\nssm.exe")
        return False
    
    # Create the DistPlatformAgent service
    print(f"Creating service 'DistPlatformAgent'...")
    subprocess.run([nssm, "install", "DistPlatformAgent", python, hidden_service], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "AppDirectory", script_dir], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "DisplayName", "Distributed Computing Platform Agent"], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "Description", "Runs permanently in background. Controls this computer remotely."], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "Start", "AUTO"], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "AppNoConsole", "1"], check=True)
    
    # Create the listener service
    print(f"Creating service 'DistPlatformListener'...")
    listener_script = os.path.join(script_dir, "agent_listener.py")
    subprocess.run([nssm, "install", "DistPlatformListener", python, listener_script], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "AppDirectory", script_dir], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "DisplayName", "Distributed Platform Job Listener"], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "Description", "Receives and executes jobs from the cluster."], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "Start", "AUTO"], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "AppNoConsole", "1"], check=True)
    
    print()
    print("=" * 50)
    print("  SERVICES INSTALLED SUCCESSFULLY!")
    print("=" * 50)
    print()
    print("The agent now runs as a Windows service:")
    print("  - Starts automatically when Windows boots")
    print("  - Runs completely hidden (no visible window)")
    print("  - No terminal window ever needed")
    print("  - Completely invisible on the computer")
    print()
    print("Commands:")
    print("  Start:   nssm start DistPlatformAgent")
    print("  Stop:    nssm stop DistPlatformAgent")
    print("  Remove:  nssm remove DistPlatformAgent confirm")
    print()
    print("To start both services now:")
    print("  nssm start DistPlatformAgent")
    print("  nssm start DistPlatformListener")
    print()
    return True

if __name__ == "__main__":
    create_windows_service()
