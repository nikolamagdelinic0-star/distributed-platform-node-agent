"""
Node Agent - Lightweight background service for Windows nodes.

This agent runs on authorized Windows computers and provides:
- Node registration and heartbeat
- Resource monitoring
- Remote desktop support
- Job execution
- File transfer
- AI runtime adapter

Target: Windows 10 and Windows 11
"""

import os
import sys
import json
import time
import logging
import threading
import socket
import platform
import uuid
import subprocess
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests
import psutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("node-agent")

AGENT_VERSION = "1.0.0"
HEARTBEAT_INTERVAL = int(os.environ.get("DP_HEARTBEAT_INTERVAL", "10"))

# Read controller URL from config file
CONFIG_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / "agent_config.txt"

def load_config():
    """Load agent configuration from file."""
    controller_url = "http://localhost:8000"
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    if key.strip() == "CONTROLLER_URL":
                        controller_url = value.strip()
    return controller_url

NODE_ID_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / ".node_id"
CREDENTIALS_FILE = Path(os.path.dirname(os.path.abspath(__file__))) / ".node_credentials"


def get_node_id():
    """Get or generate permanent node ID."""
    if NODE_ID_FILE.exists():
        return NODE_ID_FILE.read_text().strip()
    node_id = f"node-{uuid.uuid4().hex[:12]}"
    NODE_ID_FILE.write_text(node_id)
    return node_id


def get_credentials():
    """Get or generate node credentials."""
    if CREDENTIALS_FILE.exists():
        return CREDENTIALS_FILE.read_text().strip()
    creds = hashlib.sha256(os.urandom(32)).hexdigest()
    CREDENTIALS_FILE.write_text(creds)
    return creds


class HardwareDetector:
    """Detect available hardware on Windows."""

    @staticmethod
    def detect():
        info = {}
        info["cpu_model"] = platform.processor() or "Unknown"
        info["cpu_cores"] = psutil.cpu_count(logical=False) or 1
        info["logical_processors"] = psutil.cpu_count(logical=True) or 1
        info["cpu_utilization"] = psutil.cpu_percent(interval=1)

        mem = psutil.virtual_memory()
        info["total_ram"] = mem.total
        info["available_ram"] = mem.available

        disk = psutil.disk_usage("/")
        info["storage_capacity"] = disk.total
        info["free_storage"] = disk.free

        info["gpu_model"] = HardwareDetector._get_gpu()
        info["gpu_vram"] = HardwareDetector._get_gpu_vram()
        info["gpu_utilization"] = HardwareDetector._get_gpu_util()
        info["gpu_temperature"] = HardwareDetector._get_gpu_temp()

        info["network_latency"] = HardwareDetector._get_latency()
        info["network_bandwidth_estimate"] = HardwareDetector._get_bandwidth()

        info["os_name"] = platform.system()
        info["os_version"] = platform.version()

        return info

    @staticmethod
    def _get_gpu():
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_videocontroller", "get", "name"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line and "Name" not in line and line != "":
                    return line
        except Exception:
            pass
        return None

    @staticmethod
    def _get_gpu_vram():
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_videocontroller", "get", "adapterram"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.strip().split("\n"):
                try:
                    val = int(line.strip())
                    if val > 0:
                        return val
                except ValueError:
                    continue
        except Exception:
            pass
        return 0

    @staticmethod
    def _get_gpu_util():
        try:
            return 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _get_gpu_temp():
        return None

    @staticmethod
    def _get_latency():
        try:
            import time
            controller_host = CONTROLLER_URL.replace("http://", "").replace("https://", "").split("/")[0]
            start = time.time()
            socket.create_connection((controller_host, 80), timeout=2)
            return (time.time() - start) * 1000
        except Exception:
            return 999.0

    @staticmethod
    def _get_bandwidth():
        try:
            net_io = psutil.net_io_counters()
            time.sleep(0.5)
            net_io2 = psutil.net_io_counters()
            return ((net_io2.bytes_sent + net_io2.bytes_recv) - (net_io.bytes_sent + net_io.bytes_recv)) / 0.5
        except Exception:
            return 0


class HeartbeatManager:
    """Manage node heartbeats to the controller."""

    def __init__(self, node_id, credentials, controller_url):
        self.node_id = node_id
        self.credentials = credentials
        self.controller_url = controller_url
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _heartbeat_loop(self):
        while self.running:
            try:
                self.send_heartbeat()
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
            time.sleep(HEARTBEAT_INTERVAL)

    def send_heartbeat(self):
        hardware = HardwareDetector.detect()
        payload = {
            "type": "heartbeat",
            "node_id": self.node_id,
            "status": "ONLINE",
            "agent_version": AGENT_VERSION,
            "hardware": hardware,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            resp = requests.post(
                f"{self.controller_url}/api/v1/nodes/heartbeat",
                json=payload,
                headers={"Authorization": f"Bearer {self.credentials}"},
                timeout=10
            )
            if resp.status_code not in (200, 201):
                logger.warning(f"Heartbeat returned {resp.status_code}")
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")

    def send_metrics(self):
        hardware = HardwareDetector.detect()
        payload = {
            "type": "metrics",
            "node_id": self.node_id,
            "metrics": hardware,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            requests.post(
                f"{self.controller_url}/api/v1/nodes/metrics",
                json=payload,
                headers={"Authorization": f"Bearer {self.credentials}"},
                timeout=10
            )
        except Exception as e:
            logger.error(f"Metrics error: {e}")


class NodeAgent:
    """Main node agent."""

    def __init__(self):
        self.node_id = get_node_id()
        self.credentials = get_credentials()
        self.controller_url = load_config()
        self.running = False
        self.heartbeat = HeartbeatManager(self.node_id, self.credentials, self.controller_url)
        self.current_job = None
        logger.info(f"Controller URL: {self.controller_url}")

    def start(self):
        self.running = True
        logger.info(f"Node Agent starting on {self.node_id}")
        logger.info(f"Hardware: {json.dumps(HardwareDetector.detect(), indent=2)}")
        self.heartbeat.start()
        logger.info("Node Agent started successfully")

    def stop(self):
        self.running = False
        self.heartbeat.stop()
        logger.info("Node Agent stopped")


if __name__ == "__main__":
    agent = NodeAgent()
    try:
        agent.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()
        logger.info("Node Agent terminated")

# ──────────────────────────────────────────────────────────────────────
# Remote Desktop Module
# ──────────────────────────────────────────────────────────────────────

class RemoteDesktopServer:
    """Simple remote desktop using WebSocket."""
    
    def __init__(self, agent):
        self.agent = agent
        self.clients = []
    
    def capture_screen(self):
        """Capture the Windows screen as bytes."""
        try:
            import mss
            import numpy as np
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                img = np.array(sct.grab(monitor))
                # Convert to PNG bytes
                from PIL import Image
                import io
                pil_img = Image.fromarray(img)
                buf = io.BytesIO()
                pil_img.save(buf, format='PNG')
                return buf.getvalue()
        except Exception as e:
            logger.error(f"Screen capture failed: {e}")
            return None
    
    def start_server(self, port=8765):
        """Start a simple WebSocket server for remote desktop."""
        import asyncio
        import websockets
        
        async def handler(websocket, path):
            async for message in websocket:
                data = json.loads(message)
                if data.get("type") == "capture":
                    img_bytes = self.capture_screen()
                    if img_bytes:
                        await websocket.send(img_bytes)
                elif data.get("type") == "input":
                    self._handle_input(data.get("input"))
        
        self.ws_server = websockets.serve(handler, "0.0.0.0", port)
        logger.info(f"Remote desktop server on port {port}")
    
    def _handle_input(self, input_data):
        """Handle mouse/keyboard input."""
        try:
            from pynput.mouse import Controller as MouseController
            from pynput.keyboard import Controller as KeyboardController
            if input_data.get("type") == "mouse":
                mouse = MouseController()
                mouse.position = (input_data["x"], input_data["y"])
                if input_data.get("action") == "click":
                    mouse.click(input_data.get("button", "left"))
            elif input_data.get("type") == "keyboard":
                keyboard = KeyboardController()
                if input_data.get("action") == "press":
                    keyboard.press(input_data.get("key"))
                elif input_data.get("action") == "release":
                    keyboard.release(input_data.get("key"))
        except Exception as e:
            logger.error(f"Input handling failed: {e}")
