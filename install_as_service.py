"""Install the node agent as a permanent Windows service."""
import os
import sys
import subprocess
import shutil

def install():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agent_py = os.path.join(script_dir, "agent.py")
    listener_py = os.path.join(script_dir, "agent_listener.py")
    python = sys.executable
    
    print("Checking for nssm...")
    nssm = shutil.which("nssm")
    if not nssm:
        print("nssm not found. Downloading...")
        try:
            url = "https://nssm.cc/release/nssm-2.24.zip"
            urllib.request.urlretrieve(url, "/tmp/nssm.zip")
            import zipfile
            with zipfile.ZipFile("/tmp/nssm.zip") as z:
                z.extractall("/tmp/nssm")
            # Find nssm.exe
            for root, dirs, files in os.walk("/tmp/nssm"):
                for f in files:
                    if f == "nssm.exe":
                        nssm = os.path.join(root, f)
                        break
        except Exception as e:
            print(f"Failed to download nssm: {e}")
            print("Manual install: download nssm from https://nssm.cc")
            return
    
    # Install main agent as service
    subprocess.run([nssm, "install", "DistPlatformAgent", python, agent_py], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "AppDirectory", script_dir], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "DisplayName", "Distributed Platform Agent"], check=True)
    subprocess.run([nssm, "set", "DistPlatformAgent", "Start", "AUTO"], check=True)
    
    # Install job listener as service
    subprocess.run([nssm, "install", "DistPlatformListener", python, listener_py], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "AppDirectory", script_dir], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "DisplayName", "Distributed Platform Job Listener"], check=True)
    subprocess.run([nssm, "set", "DistPlatformListener", "Start", "AUTO"], check=True)
    
    print("\nBoth services installed!")
    print("To start: nssm start DistPlatformAgent && nssm start DistPlatformListener")
    print("To stop: nssm stop DistPlatformAgent && nssm stop DistPlatformListener")
    print("To remove: nssm remove DistPlatformAgent confirm && nssm remove DistPlatformListener confirm")

if __name__ == "__main__":
    import urllib.request
    install()
