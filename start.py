"""Simple starter script for the node agent."""
import os
import sys
import subprocess

# Get the directory of this script
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)

# Run the agent
subprocess.run([sys.executable, "agent.py"])
