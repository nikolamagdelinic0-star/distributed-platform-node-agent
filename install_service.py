"""Install the node agent as a Windows service."""
import sys
import os
import subprocess

def install_service():
    """Install node-agent as a Windows service using nssm."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    agent_script = os.path.join(script_dir, "node-agent", "agent.py")
    service_name = "DistributedPlatformAgent"
    service_display = "Distributed Computing Platform Agent"
    
    # Check if nssm is available
    try:
        result = subprocess.run(['nssm', '--version'], capture_output=True, text=True)
        print(f"nssm found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("nssm not found. Downloading...")
        # Download nssm
        url = "https://nssm.cc/release/nssm-2.24.zip"
        import urllib.request
        import zipfile
        import io
        
        print("Downloading nssm...")
        urllib.request.urlretrieve(url, "/tmp/nssm.zip")
        with zipfile.ZipFile("/tmp/nssm.zip") as z:
            z.extractall("/tmp/nssm")
        nssm_path = "/tmp/nssm/win64/nssm.exe"
        if not os.path.exists(nssm_path):
            nssm_path = "/tmp/nssm/nssm-2.24/nssm.exe"
        print(f"nssm extracted to: {nssm_path}")
    
    # Install the service
    python_path = sys.executable
    if not python_path:
        python_path = "python"
    
    print(f"Installing service '{service_name}'...")
    subprocess.run(['nssm', 'install', service_name, python_path, agent_script], check=True)
    subprocess.run(['nssm', 'set', service_name, 'AppDirectory', script_dir], check=True)
    subprocess.run(['nssm', 'set', service_name, 'AppParameters', ''], check=True)
    subprocess.run(['nssm', 'set', service_name, 'DisplayName', service_display], check=True)
    subprocess.run(['nssm', 'set', service_name, 'Start', 'AUTO'], check=True)
    
    print(f"Service '{service_name}' installed!")
    print(f"Start it with: nssm start {service_name}")
    print(f"Stop it with: nssm stop {service_name}")
    print(f"Remove it with: nssm remove {service_name} confirm")

if __name__ == "__main__":
    install_service()
