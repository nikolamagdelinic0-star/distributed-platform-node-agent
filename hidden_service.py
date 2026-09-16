"""Hidden Windows Service Runner — no visible window, runs permanently."""
import sys
import os
import subprocess
import time
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.log"),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("hidden-service")

def run_agent_hidden():
    """Run the agent with no visible window."""
    agent_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent.py")
    listener_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_listener.py")
    
    # Start agent in hidden mode
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0  # Hidden window
    
    # Start agent
    logger.info("Starting hidden agent...")
    agent_proc = subprocess.Popen(
        [sys.executable, agent_script],
        startupinfo=startupinfo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL
    )
    
    # Start listener
    logger.info("Starting hidden listener...")
    listener_proc = subprocess.Popen(
        [sys.executable, listener_script],
        startupinfo=startupinfo,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL
    )
    
    logger.info(f"Agent PID: {agent_proc.pid}, Listener PID: {listener_proc.pid}")
    
    # Keep running
    try:
        while True:
            time.sleep(10)
            if agent_proc.poll() is not None:
                logger.warning("Agent died, restarting...")
                agent_proc = subprocess.Popen(
                    [sys.executable, agent_script],
                    startupinfo=startupinfo,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
                )
            if listener_proc.poll() is not None:
                logger.warning("Listener died, restarting...")
                listener_proc = subprocess.Popen(
                    [sys.executable, listener_script],
                    startupinfo=startupinfo,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
                )
    except KeyboardInterrupt:
        agent_proc.terminate()
        listener_proc.terminate()

if __name__ == "__main__":
    run_agent_hidden()
