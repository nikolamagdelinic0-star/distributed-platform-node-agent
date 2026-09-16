"""Wake-on-LAN handler — keeps the computer responsive to remote power-on."""
import logging
import subprocess
import os
import json
import time
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wol-handler")

class WoLHandler:
    """Handle Wake-on-LAN magic packets."""
    
    def __init__(self):
        self.mac_address = self._get_mac()
        self.running = False
        self.listener_thread = None
    
    def _get_mac(self):
        """Get the MAC address of the primary network interface."""
        try:
            import psutil
            addrs = psutil.net_if_addrs()
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family.name == 'AF_LINK' or addr.family == 17:
                        return addr.address.replace(':', '-').upper()
            # Fallback: get MAC from ipconfig
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split('\n'):
                if 'Physical' in line and ':' in line:
                    mac = line.split(':')[-1].strip().replace('-', ':').upper()
                    if len(mac) == 17:
                        return mac
        except Exception as e:
            logger.error(f"Failed to get MAC: {e}")
        return None
    
    def send_magic_packet(self, mac):
        """Send a Wake-on-LAN magic packet to wake the computer."""
        try:
            from wakeonlan import send_magic_packet
            send_magic_packet(mac)
            logger.info(f"Magic packet sent to {mac}")
            return True
        except Exception as e:
            logger.error(f"Failed to send magic packet: {e}")
            # Fallback: construct and send manually
            try:
                mac_bytes = bytes.fromhex(mac.replace(':', '').replace('-', ''))
                magic = b'\xff' * 6 + mac_bytes * 16
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(magic, ('255.255.255.255', 9))
                sock.close()
                logger.info(f"Magic packet sent manually to {mac}")
                return True
            except Exception as e2:
                logger.error(f"Fallback WoL also failed: {e2}")
                return False
    
    def listen_for_wol(self):
        """Listen for incoming magic packets (if the computer supports WoL in sleep/off state)."""
        self.running = True
        logger.info("WoL listener started")
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('0.0.0.0', 9))
            while self.running:
                data, addr = sock.recvfrom(102)
                if data[:6] == b'\xff' * 6:
                    logger.info(f"Received magic packet from {addr}")
                    self._trigger_power_on()
        except Exception as e:
            logger.error(f"WoL listener error: {e}")
    
    def _trigger_power_on(self):
        """Trigger the computer to power on (via WoL in BIOS)."""
        logger.info("Magic packet received! Computer should wake up.")
        # In BIOS-enabled WoL, the network card receives the magic packet
        # and sends a power-on signal to the motherboard
    
    def start(self):
        """Start WoL listener in background."""
        self.listener_thread = threading.Thread(target=self.listen_for_wol, daemon=True)
        self.listener_thread.start()
        logger.info("WoL handler started")
    
    def stop(self):
        self.running = False

wol_handler = None

if __name__ == "__main__":
    handler = WoLHandler()
    handler.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handler.stop()
