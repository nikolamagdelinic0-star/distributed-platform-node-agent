"""
Node Agent Installer for Windows.

Creates a Windows service for the node agent so it runs as a background service.
Usage: python installer.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def install_service():
    """Install the node agent as a Windows service."""
    try:
        import pywin32
    except ImportError:
        print("Installing pywin32...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pywin32"])
        import pywin32

    agent_path = Path(__file__).parent / "agent.py"
    service_name = "DistributedPlatformNode"
    service_display = "Distributed Computing Platform Node Agent"

    print(f"Installing {service_display}...")
    print(f"Agent path: {agent_path}")

    # Register the service
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    import threading

    class NodeAgentService(win32serviceutil.ServiceFramework):
        _svc_name_ = service_name
        _svc_display_name_ = service_display
        _svc_description_ = "Manages distributed computing platform node operations"

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
            self.running = True

        def SvcStop(self):
            self.running = False
            win32event.SetEvent(self.hWaitStop)

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (service_name, "Node agent starting")
            )
            # Run the agent
            os.system(f'"{sys.executable}" "{agent_path}"')
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STOPPED,
                (service_name, "Node agent stopped")
            )

    # Register the service
    if hasattr(win32serviceutil, "InstallService"):
        win32serviceutil.InstallService(
            NodeAgentService.__module__,
            service_name,
            service_display_name,
            startType=win32service.SERVICE_AUTO_START
        )
        print(f"Service '{service_name}' installed successfully!")
        print(f"Start it with: net start {service_name}")
        print(f"Stop it with: net stop {service_name}")
    else:
        print("Could not install as service. Running as background process instead.")

    # Start the agent
    subprocess.Popen([sys.executable, str(agent_path)])
    print("Node agent started!")


def uninstall_service():
    """Uninstall the node agent Windows service."""
    try:
        import win32serviceutil
        win32serviceutil.RemoveService(service_name)
        print("Service uninstalled.")
    except ImportError:
        print("pywin32 not available. Cannot uninstall service.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "uninstall":
        uninstall_service()
    else:
        install_service()
